# Stillness Timer Backend

A simple Flask API that tracks meditation/stillness session durations and provides encouraging feedback based on user percentiles.

## Features

- 📊 **Session Tracking**: Accepts session durations and stores them by date
- 🏆 **Percentile Calculation**: Compares users against others from the same day
- 💬 **Encouraging Messages**: Returns personalized feedback based on performance
- 💾 **Persistent Storage**: Saves data to JSON file (survives server restarts)
- 🌐 **CORS Enabled**: Ready for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python backend.py
```

Server will start at `http://localhost:5000`

### 3. Test the API

```bash
# Run the test script
python test_backend.py
```

## API Endpoints

### POST `/api/session`

Submit a meditation session duration.

**Request Body:**
```json
{
    "duration": 300,
    "timestamp": "2024-01-15T10:30:00"
}
```

**Response:**
```json
{
    "message": "🌟 Well done! You achieved more stillness than 75% of users today (5m 0s).",
    "duration": 300,
    "percentile": 75,
    "sessions_today": 8,
    "total_sessions": 42
}
```

### GET `/api/stats`

Get current statistics.

**Response:**
```json
{
    "today": {
        "sessions": 8,
        "average": 245.5,
        "longest": 1800
    },
    "all_time": {
        "total_sessions": 42,
        "average": 198.7,
        "longest": 3600
    }
}
```

### GET `/`

Health check endpoint.

## Message Examples

The API returns different encouraging messages based on percentile:

- **95%+**: "🏆 Exceptional stillness! You outlasted 97% of users today..."
- **90%+**: "⭐ Incredible discipline! You were more still than 92% of users..."
- **75%+**: "🌟 Well done! You achieved more stillness than 78% of users..."
- **50%+**: "✨ Good work! You were more still than 63% of users..."
- **25%+**: "🌱 Every moment of stillness counts. You lasted 2m 15s..."
- **<25%**: "🤲 Stillness is a practice. Your 45s is a beautiful start..."

## Data Storage

- Sessions are stored in memory while the server runs
- Data persists to `session_data.json` file
- Data survives server restarts
- Sessions are grouped by date for daily percentile calculations

## Frontend Integration

To use with your frontend timer:

```javascript
// When user's session ends
async function submitSession(durationInSeconds) {
    try {
        const response = await fetch('http://localhost:5000/api/session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                duration: durationInSeconds,
                timestamp: new Date().toISOString()
            })
        });
        
        const data = await response.json();
        
        // Show the encouraging message to user
        console.log(data.message);
        
    } catch (error) {
        console.error('Error submitting session:', error);
    }
}
```

## Development

The backend uses:
- **Flask**: Lightweight web framework
- **Flask-CORS**: Cross-origin requests support
- **JSON**: Simple file-based storage
- **In-memory**: Fast session lookups

## Deployment

For production deployment:
1. Use a proper database (PostgreSQL, MongoDB, etc.)
2. Add authentication/rate limiting
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Add logging and monitoring
5. Set up proper environment configuration

## Testing

Run the test script to see various session durations and responses:

```bash
python test_backend.py
```

This will submit several test sessions and show you the different types of encouraging messages the API generates.

---

**Built for the minimalist timer project** 🧘