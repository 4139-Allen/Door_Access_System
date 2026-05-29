
#include "stm32f10x.h"

#include "string.h"
#include "stdio.h"

#include "usart.h"
#include "timer.h"
#include "delay.h"

#include "rc522_config.h"
#include "rc522_function.h"
#include "Martix_KEY.h"
#include "General_Module.h"
#include "lcd12864.h"
#include "AT24CXX.h"
#include "AS608.h"

#include "password.h"
#include "menu.h"

#define COMM_MODE_ESP8266   1
#define COMM_MODE_W5500     2

#define COMM_MODE   COMM_MODE_ESP8266

GeneralModule Buzzer =
	{
		.GPIOx = GPIOB,
		.GPIO_Pin = GPIO_Pin_1,
	};

GeneralModule Relay =
	{
		.GPIOx = GPIOB,
		.GPIO_Pin = GPIO_Pin_11,
	};

#if COMM_MODE == COMM_MODE_W5500
#include "w5500.h"
#include "mqtt_client.h"

static w5500_netinfo_t netcfg = {
    .mac     = {0x02, 0x00, 0x00, 0x00, 0x00, 0x01},
    .ip      = {172, 26, 20, 201},         // STM32设备IP（同网段）
    .gateway = {172, 26, 20, 100},           // 恢复之前的配置
    .subnet  = {255, 255, 248, 0},         // 与WiFi相同的子网掩码
};

static uint8_t mqtt_broker_ip[4] = {172, 26, 20, 100};  // 有线网卡IP（直连）
static uint16_t mqtt_broker_port = 1883;

#define DEVICE_ID   "001"

mqtt_client_t mqtt;
static uint8_t  w5500_ready = 0;
static uint32_t last_ping_ms = 0;
static uint32_t last_heartbeat_ms = 0;

static void on_mqtt_message(char *topic, uint8_t *payload, uint16_t len)
{
    if (len == 9 && memcmp(payload, "OPEN_DOOR", 9) == 0)
    {
        GeneralModule_Write(&Relay, 1);     // ���ϼ̵��������ţ�
        W5500_DelayMs(500);
        GeneralModule_Write(&Relay, 0);     // �Ͽ��̵��������ţ�
        MQTT_Publish(&mqtt, "door/" DEVICE_ID "/status", (uint8_t *)"OK", 2);
    }
}
#endif

volatile uint32_t system_tick_ms = 0;

uint8_t Read_UID(uint8_t *UID);

uint8_t RC522_UID[4];
uint8_t RC522_UID_Save[4];

int main(void)
{
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO, ENABLE);
	GPIO_PinRemapConfig(GPIO_Remap_SWJ_JTAGDisable, ENABLE);
	delay_init();
	uart_init(9600);
	uart2_init(57600);
	PS_StaGPIO_Init();
	GeneralModule_Init(&Buzzer, GPIO_Mode_Out_PP);
	GPIO_SetBits(Buzzer.GPIOx, Buzzer.GPIO_Pin);
	GeneralModule_Init(&Relay, GPIO_Mode_Out_PP);
	MartixKEY_Init();
	lcd_init();

	AT24CXX_Init();
	lcd_draw_str(0, 0, "Init EEPROM...");
	while (AT24CXX_Check())
	{
		lcd_draw_str(1, 0, "EEPROM FAIL!");
	}
	lcd_draw_str(0, 0, "                                                                ");
	lcd_draw_str(0, 0, "System Init...");
	Password_Read(0);
	AT24CXX_Read(0x50, RC522_UID_Save, 4);
	lcd_draw_str(0, 0, "                                                                ");

	RC522_Init();
	PcdReset();
	PcdAntennaOff();
	delay_ms(100);
	PcdAntennaOn();

	Timer2_Init(1999, 719);

#if COMM_MODE == COMM_MODE_W5500
	printf("[DBG] W5500 GPIO init...\n");
	W5500_GPIO_Init();
	
	// 手动执行复位并验证
	printf("[DBG] W5500: Manual reset and verify...\n");
	W5500_Reset();
	W5500_DelayMs(150);
	
	// 验证复位后版本号
	uint8_t ver_check = W5500_ReadByte(W5500_VERSION);
	printf("[DBG] W5500: Post-reset VERSION = 0x%02X (expected 0x04)\n", ver_check);
	if (ver_check != 0x04) {
		printf("[ERR] W5500: Reset FAILED! Chip not responding. Check hardware!\n");
		while(1); // 停止执行
	}
	
	W5500_Init(&netcfg);
	lcd_draw_str(2, 0, "W5500 Init...");
	W5500_DelayMs(500);
	printf("[DBG] W5500 Init done, connecting MQTT...\n");

	// W5500 自检: 读版本号寄存器 (W5500_VERSION, 返回 0x04)
	uint8_t ver = W5500_ReadByte(W5500_VERSION);
	printf("[DBG] W5500 VERSION register = 0x%02X (expected 0x04)\n", ver);

	// SPI 读写测试：写入一个已知值然后读回验证
	printf("[TEST] SPI Read/Write Test:\n");
	{
		uint16_t test_addr = W5500_ADDR(0x00, 0x1C);  // PTMR 寄存器（可读写）
		uint8_t write_val = 0xA5;
		uint8_t read_val;
		
		printf("[TEST] Writing 0x%02X to PTMR...\n", write_val);
		W5500_WriteByte(test_addr, write_val);
		W5500_DelayMs(10);
		
		read_val = W5500_ReadByte(test_addr);
		printf("[TEST] Read back from PTMR: 0x%02X\n", read_val);
		
		if (read_val == write_val) {
			printf("[TEST] ✓ SPI R/W test PASSED\n");
		} else {
			printf("[TEST] ✗ SPI R/W test FAILED! (wrote 0x%02X, read 0x%02X)\n", write_val, read_val);
			printf("[TEST] This indicates SPI communication problem!\n");
		}
	}

	// TX缓冲区诊断测试
	printf("\n[MAIN] About to call W5500_Diagnose_TX_Buffer...\n");
	W5500_Diagnose_TX_Buffer();
	printf("[MAIN] Diagnosis finished!\n\n");

	// ---- SPI TX BUFFER VERIFICATION TEST (已注释，避免干扰MQTT) ----
	/*
	{
		uint8_t test_sock = 0;
		uint8_t write_data[32];
		uint8_t read_back[32];
		uint16_t i, errors = 0;

		for (i = 0; i < sizeof(write_data); i++) write_data[i] = i + 1;

		printf("[TEST] Opening socket 0 and writing 32 bytes to TX buffer...\n");
		if (W5500_Socket_Open(test_sock, Sn_MR_TCP))
		{
			printf("[TEST] Writing 32 bytes to Sn_TXBUF(0)...\n");
			W5500_Write(Sn_TXBUF(test_sock), write_data, sizeof(write_data));
			W5500_DelayMs(10);

			printf("[TEST] Reading back 32 bytes from Sn_TXBUF(0): ");
			W5500_Read(Sn_TXBUF(test_sock), read_back, sizeof(read_back));
			for (i = 0; i < sizeof(read_back); i++) {
				printf("%02X ", read_back[i]);
				if (read_back[i] != write_data[i]) errors++;
			}
			printf("\n[TEST] Errors: %u / %u\n", errors, (uint16_t)sizeof(write_data));

			W5500_Socket_Close(test_sock);
		}
		else printf("[TEST] Socket OPEN FAILED\n");
	}
	*/
#endif

	while (1)
	{
		menu();
		key_handle();

	#if COMM_MODE == COMM_MODE_ESP8266
		if (rx_finish_flag)
		{
			rx_finish_flag = 0;

			if (rx_cnt == 10 && memcmp(rx_buf, "OPEN_DOOR\n", 10) == 0)
			{
				GeneralModule_Write(&Relay, 1);
				delay_ms(500);
				GeneralModule_Write(&Relay, 0);

				USART_SendData(USART1, 'O');
				while (USART_GetFlagStatus(USART1, USART_FLAG_TC) == RESET);
				USART_SendData(USART1, 'K');
				while (USART_GetFlagStatus(USART1, USART_FLAG_TC) == RESET);
				USART_SendData(USART1, '\n');
				while (USART_GetFlagStatus(USART1, USART_FLAG_TC) == RESET);
			}

			memset(rx_buf, 0, rx1_buf_size);
			rx_cnt = 0;
		}

	#elif COMM_MODE == COMM_MODE_W5500
		if (w5500_ready)
		{
			if (!MQTT_Loop(&mqtt))
			{
				W5500_Socket_Close(mqtt.sock);
				W5500_DelayMs(1000);
				w5500_ready = 0;
			}
			else
			{
				if (system_tick_ms - last_ping_ms >= 30000)
				{
					last_ping_ms = system_tick_ms;
					MQTT_PingReq(&mqtt);
				}
				if (system_tick_ms - last_heartbeat_ms >= 60000)
				{
					last_heartbeat_ms = system_tick_ms;
					MQTT_Publish(&mqtt, "door/" DEVICE_ID "/status", (uint8_t *)"ONLINE", 6);
				}
			}
		}
		else
		{
			// 尝试 Socket 1（需要先硬件复位清除 CLOSE_WAIT 状态）
			static uint8_t reset_count = 0;

			if (MQTT_Connect(&mqtt, 1, mqtt_broker_ip, mqtt_broker_port, DEVICE_ID, on_mqtt_message))
			{
				MQTT_Subscribe(&mqtt, "door/" DEVICE_ID "/command");
				MQTT_Publish(&mqtt, "door/" DEVICE_ID "/status", (uint8_t *)"ONLINE", 6);
				w5500_ready = 1;
				reset_count = 0;
			}
			else
			{
				reset_count++;
				printf("[WARN] MQTT connect failed (count=%d), reinitializing W5500...\n", reset_count);

				// 重新初始化 W5500
				W5500_Reset();
				W5500_Init(&netcfg);
				W5500_DelayMs(500);

				// 重新读取 VERSION 确认 W5500 正常
				uint8_t ver = W5500_ReadByte(W5500_VERSION);
				printf("[DBG] W5500 VERSION after reset = 0x%02X\n", ver);

				W5500_DelayMs(2000);
			}
		}
	#endif
	}
}

uint8_t Read_UID(uint8_t *UID)
{
	uint8_t sta = 1;
	uint8_t ucArray_ID[4];
	uint8_t ucStatusReturn = 0;

	ucStatusReturn = PcdRequest(PICC_REQALL, ucArray_ID);
	if (ucStatusReturn == MI_OK)
	{
		if (PcdAnticoll(UID) == MI_OK)
		{
			sta = 0;
		}
	}
	PcdHalt();

	return sta;
}

void TIM2_IRQHandler(void)
{
	if (TIM_GetITStatus(TIM2, TIM_IT_Update) == SET)
	{
		Get_Key();
		system_tick_ms += 20;
		TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
	}
}
