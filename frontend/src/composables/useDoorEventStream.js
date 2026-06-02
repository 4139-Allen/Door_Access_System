import { reactive } from 'vue'

const MAX_EVENTS = 50

const eventList = reactive([])

export function useDoorEventStream() {
  function addDoorEvent(event) {
    eventList.unshift({
      id: Date.now() + Math.random(),
      username: event.username,
      device_name: event.device_name,
      location: event.location || '',
      action: event.action || '开门',
      timestamp: event.timestamp
    })
    if (eventList.length > MAX_EVENTS) {
      eventList.splice(MAX_EVENTS)
    }
  }

  return {
    eventList,
    addDoorEvent
  }
}
