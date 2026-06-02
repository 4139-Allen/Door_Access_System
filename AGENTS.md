# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

FastAPI + Vue 3 door access management system with JWT auth, device management, access logs, WebSocket real-time updates, and AI-powered natural language door control (DeepSeek integration).

## Architecture

Three-layer backend architecture:

```
api/        (FastAPI routers) -> services/     (business logic) -> database/models/  (SQLAlchemy)
utils/      (auth, response, exceptions, logger)
schemas/    (Pydantic validation)
core/       (config, AI system prompt)
```

- **API layer** (`api/*.py`): FastAPI routers, receives requests, calls service layer, returns unified `{code, msg, data}` responses via `utils/response.py`
- **Service layer** (`services/*.py`): Business logic, throws exceptions (ValueError, PermissionError) that `@handle_api_exception` catches
- **Data layer** (`database/models/*.py`): SQLAlchemy ORM models (User, Device, UserDevice, DoorLog)
- **Auth** (`utils/auth.py`): JWT tokens with Redis-backed token validation + blacklist mechanism
- **Dependency injection**: FastAPI `Depends()` for DB sessions (`get_db`), current user (`get_current_user_obj`), and admin validation (`require_admin`)
- **Frontend** (`frontend/`): Vue 3 + Element Plus, Vite build tool, routes protected by navigation guard checking `localStorage.token`

## Key Conventions

- All API responses follow `{"code": int, "msg": str, "data": any}` format using `success()` and `error()` from `utils/response.py`
- API route handlers use `@handle_api_exception` decorator for automatic error-to-response conversion
- DB sessions are injected via `db: Session = Depends(get_db)`
- Admin-only endpoints use `current_user: User = Depends(require_admin)`
- Redis caching with `setex()` for device lists (60s), stats (180s), AI context (900s)
- Config from env vars via `core/config.py` loaded from `.env`

## Development Commands

```bash
# Backend - install dependencies
pip install -r requirements.txt

# Backend - run dev server (hot reload enabled)
python main.py

# Backend - run on custom host/port
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend - install dependencies
cd frontend && npm install

# Frontend - dev server (default http://localhost:5173)
cd frontend && npm run dev

# Frontend - production build (required before Docker)
cd frontend && npm run build

# Docker - full deployment
docker-compose up -d

# Docker - rebuild single service after code changes
docker-compose up -d --build fastapi
docker-compose up -d --build frontend

# Docker - view logs
docker-compose logs -f fastapi
```

## Important Notes

- Docker `.env` must use service names (`MYSQL_HOST=mysql`, `REDIS_HOST=redis`), not `localhost`
- Frontend must be built (`npm run build`) before Docker deployment
- Admin account auto-created on first start (configurable via `ADMIN_USERNAME`/`ADMIN_PASSWORD` in `.env`)
- AI features are optional; missing `DEEPSEEK_API_KEY` logs a warning but doesn't block startup
- Cache invalidation: device list cache keyed by `cache:device:list:user:{user_id}`, invalidate on device CRUD
- Logs go to `logs/app.log.YYYY-MM-DD` with 30-day rotation

## Database Models

### User Model (`database/models/user.py`)
- `id`: Integer, primary key, indexed
- `username`: String(50), unique, indexed
- `password`: String(100), bcrypt hashed (72-byte limit)
- `role`: String(20), default "user" (options: "admin", "user")
- `created_at`: DateTime, auto-generated with `datetime.now`

### Device Model (`database/models/device.py`)
- `id`: Integer, primary key, indexed
- `name`: String(100), device name/number (e.g., "001", "002")
- `status`: String(20), default "offline" (options: "online", "offline")
- `location`: String(200), device location description
- `created_at`: DateTime, auto-generated
- `updated_at`: DateTime, auto-updated on change

### DoorLog Model (`database/models/door_log.py`)
- `id`: Integer, primary key, indexed
- `user_id`: Integer, foreign key to User.id
- `device_id`: Integer, foreign key to Device.id
- `action`: String(50), action description (e.g., "开门")
- `status`: String(50), result status (e.g., "成功", "失败：无权限")
- `time`: DateTime, auto-generated

### UserDevice Model (`database/models/user_device.py`)
- `id`: Integer, primary key, indexed
- `user_id`: Integer, foreign key to User.id (with CASCADE delete)
- `device_id`: Integer, foreign key to Device.id (with CASCADE delete, indexed)

## API Endpoints

### Authentication
- `POST /auth/login` - User login with username/password
- `POST /auth/register` - User registration (creates regular user)
- `POST /auth/logout` - Logout and invalidate token
- `PUT /auth/password` - Change current user's password

### User Management (Admin Only)
- `GET /users?page=1&size=10&username=&role=` - Get paginated user list with filters
- `POST /users` - Create new user
- `DELETE /users/{user_id}` - Delete user and associated data
- `GET /users/{user_id}/devices` - Get devices bound to a specific user

### Device Management
- `POST /devices` - Create new device (Admin only)
- `GET /devices?name=` - Get device list (filtered by permission)
- `PUT /devices/{device_id}` - Update device info (Admin only)
- `DELETE /devices/{device_id}` - Delete device (Admin only, must unbind users first)
- `POST /devices/{device_id}/bind` - Bind user to device (Admin only)
- `DELETE /devices/{device_id}/unbind?user_id=` - Unbind user from device (Admin only)

### Door Control
- `POST /doors/{device_id}/open` - Open door (permission checked)
- `GET /door-logs?page=1&size=10&user_id=&device_name=&status=&start_time=&end_time=` - Query door logs

### Statistics
- `GET /statistics` - Get dashboard statistics (role-based data)

### AI Assistant
- `POST /ai/chat` - AI-powered natural language door control (Admin only)

### WebSocket
- `ws://host/ws` - Real-time door open notifications for admins

### System
- `GET /health` - Health check endpoint

## Frontend Structure

### Pages (`frontend/src/views/`)
- `Login.vue` - Login/Register page with tab switching
- `Layout.vue` - Main layout with sidebar navigation and password change dialog
- `Dashboard.vue` - Dashboard with statistics and AI chat floating button
- `Users.vue` - User management with bind/unbind functionality (Admin only)
- `Device.vue` - Device CRUD operations (Admin only)
- `Door.vue` - Door control and personal access logs
- `Log.vue` - Comprehensive door logs with advanced filtering (Admin only)

### Key Features
- Role-based menu visibility (admin vs user)
- Real-time WebSocket notifications for door opens (admins only)
- AI assistant floating button on dashboard
- Password change dialog in header
- Responsive design with Element Plus components
- Route guards checking `localStorage.token`

### State Management
- Token stored in `localStorage` as 'token'
- Role stored in `localStorage` as 'role' for UI rendering
- No Pinia/Vuex used, direct localStorage access
- Axios interceptors handle auth headers and error responses

## Configuration Details

### Required Environment Variables
- `SECRET_KEY` - JWT signing key (must be strong random string)
- `MYSQL_HOST` - Database host ("mysql" in Docker, "localhost" locally)
- `MYSQL_PASSWORD` - Database password
- `MYSQL_DB` - Database name

### Optional Environment Variables
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (default: 3600)
- `ADMIN_USERNAME` - Default admin username (default: admin)
- `ADMIN_PASSWORD` - Default admin password (default: 123456)
- `AUTO_CREATE_ADMIN` - Auto-create admin on startup (default: true)
- `DEEPSEEK_API_KEY` - DeepSeek API key for AI features
- `AI_API_URL` - AI API endpoint (default: DeepSeek URL)
- `AI_MODEL` - AI model name (default: deepseek-v4-flash)
- `AI_TIMEOUT` - AI request timeout in seconds (default: 15)
- `AI_TEMPERATURE` - AI temperature parameter (default: 0.1)
- `REDIS_HOST` - Redis host (default: 127.0.0.1)
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_DB` - Redis database number (default: 0)
- `REDIS_PASSWORD` - Redis password (optional)
- `ALLOWED_ORIGINS` - CORS allowed origins, comma-separated (default: *)

### Important Configuration Notes
- In Docker environment, use service names: `MYSQL_HOST=mysql`, `REDIS_HOST=redis`
- Locally, use: `MYSQL_HOST=localhost`, `REDIS_HOST=127.0.0.1`
- AI features are optional; system works without `DEEPSEEK_API_KEY`
- Frontend must be built before Docker deployment
- Generate secure SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Caching Strategy

### Redis Cache Keys
- `token:{token}` - Active session tokens (TTL = token expiry minutes)
- `blacklist:{token}` - Revoked tokens (TTL = 86400s / 24 hours)
- `cache:device:list:user:{user_id}` - Device list per user (TTL = 60s)
- `stat:user:{user_id}` - User statistics (TTL = 180s)
- `ai:context:user:{user_id}` - AI conversation context (TTL = 900s / 15 minutes)

### Cache Invalidation Rules
- Device cache invalidated on: create, update, delete, bind, unbind operations
- All users' device cache cleared when device is created/updated/deleted
- Individual user cache cleared when binding/unbinding devices
- Statistics cache uses TTL-based expiration only
- AI context cleared after successful door open operation

## Security Considerations

### Authentication & Authorization
- JWT tokens with Redis-backed validation
- Token blacklist mechanism for logout functionality
- Password hashing with bcrypt (72-byte limit enforced)
- Role-based access control (admin vs user)
- Admin-only endpoints protected with `require_admin` dependency
- Permission checks for door opening (admin or bound user)

### Input Validation
- Pydantic schemas for all API inputs with field validators
- Username: 1-50 chars, alphanumeric + underscore + Chinese characters
- Password: 6-72 chars minimum/maximum
- Device name/location: required fields with length limits
- SQL injection prevention via SQLAlchemy ORM

### Security Best Practices
- Never commit `.env` file to version control
- Change default admin password after first login
- Use strong SECRET_KEY in production (min 32 characters)
- Restrict `ALLOWED_ORIGINS` in production (avoid using `*`)
- Enable Redis password authentication in production
- Use HTTPS in production with proper SSL certificates
- Regular dependency updates for security patches

## Testing & Debugging

### Backend Testing
- Access Swagger UI: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: GET http://localhost:8000/health
- Check logs: `docker-compose logs -f fastapi` or view `logs/app.log.YYYY-MM-DD`
- Test API with curl: `curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"123456"}'`

### Frontend Testing
- Dev server: http://localhost:5173
- Production build serves at: http://localhost (port 80 via Nginx)
- Check browser console for WebSocket connection status
- Network tab shows API calls to http://127.0.0.1:8000 (dev) or /api/ (prod)

### Common Issues & Solutions
- **Redis connection failure**: System runs but login/logout won't work properly. Start Redis: `redis-server`
- **Database init failure**: Check MySQL credentials and connectivity. Verify MYSQL_HOST/MYSQL_PASSWORD
- **CORS errors**: Verify ALLOWED_ORIGINS configuration matches frontend URL
- **WebSocket disconnects**: Check network stability and proxy configuration in nginx.conf
- **AI not working**: Verify DEEPSEEK_API_KEY is set and valid, check network access to api.deepseek.com
- **Password too long**: bcrypt has 72-byte limit, enforce in frontend validation
- **Token expired**: Default 3600 minutes, adjust ACCESS_TOKEN_EXPIRE_MINUTES if needed
- **Frontend 404 on refresh**: Nginx config handles Vue Router history mode with try_files

### Docker Troubleshooting
- Rebuild after code changes: `docker-compose up -d --build <service_name>`
- View all logs: `docker-compose logs -f`
- Restart single service: `docker-compose restart <service_name>`
- Check container status: `docker-compose ps`
- Reset database: Stop containers, remove mysql-data volume, restart

## Development Workflow

### Adding New Feature
1. Define Pydantic schema in `schemas/`
2. Implement business logic in `services/`
3. Create API endpoint in `api/` with `@handle_api_exception`
4. Add route to `api/routers.py`
5. Update frontend in `frontend/src/views/`
6. Test with Swagger UI and frontend

### Code Style Guidelines
- Backend: Follow PEP 8, use type hints, add docstrings
- Frontend: Use Composition API (`<script setup>`), consistent component naming
- Commit messages: Use conventional commits (feat, fix, docs, style, refactor, test, chore)
- Branch strategy: main (production), develop (development), feature/* (features)

### Service Layer Pattern
- All business logic in `services/` directory
- Use `@service_exception_handler` decorator for automatic rollback
- Throw ValueError for business logic errors
- Throw PermissionError for authorization failures
- Return meaningful data or raise exceptions (don't return error dicts)

### API Layer Pattern
- Keep handlers thin, delegate to service layer
- Always use `@handle_api_exception` decorator
- Use FastAPI Depends() for dependency injection
- Return `success()` or `error()` from `utils/response.py`
- Add proper tags and descriptions to routes
