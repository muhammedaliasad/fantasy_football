# Fantasy Football Platform

A Django REST API backend for managing fantasy football teams and player transfers.

## Features

- **User Management**: Registration, login, and profile management
- **Team Management**: Automatic team generation with 20 players and $5,000,000 capital
- **Transfer Market**: List and buy players from other users
- **Transaction History**: Track all completed transfers
- **Value Appreciation**: Players increase in value (5-15%) after each transfer

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker, Docker Compose

## Quick Start

### Using Docker

```bash
# Start the application (migrations run automatically)
docker-compose up --build

# Create admin user (optional)
docker-compose exec web python manage.py createsuperuser
```

The API will be available at `http://localhost:8000`

**Note:** Migrations run automatically when the container starts. You don't need to run `migrate` manually.

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL and configure .env file
# DB_NAME=fantasy_football
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Complete API Flow

### Step 1: Register User

**POST** `/api/auth/users/register/`

```json
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "team_name": "Team Alpha"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**What happens:**
- Creates user account
- Creates a team with $5,000,000 capital
- Generates 20 players (2 GK, 5 DF, 5 MF, 8 AT) at $1,000,000 each
- Returns JWT tokens for authentication

---

### Step 2: Get Your Team

**GET** `/api/teams/my-team/`
**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": 1,
  "name": "Team Alpha",
  "capital": "5000000.00",
  "total_team_value": "20000000.00",
  "players": [
    {
      "id": 1,
      "name": "Player_GK_YXUC7L",
      "position": "GK",
      "value": "1000000.00"
    },
    // ... 19 more players
  ]
}
```

**Purpose:** View your team, capital, and all players

---

### Step 3: List a Player for Sale

**POST** `/api/transfer-listings/`
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "player_id": 1,
  "asking_price": "1500000.00"
}
```

**Response:**
```json
{
  "id": 1,  // ← listing_id for buyers to use
  "player": {
    "id": 1,
    "name": "Player_GK_YXUC7L",
    "position": "GK",
    "value": "1000000.00"
  },
  "asking_price": "1500000.00",
  "is_active": true
}
```

**Purpose:** Put a player on the transfer market. Note the `id` field - this is the `listing_id`.

---

### Step 4: Register a Second User (Buyer)

**POST** `/api/auth/users/register/`

```json
{
  "username": "user2",
  "email": "user2@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "team_name": "Team Beta"
}
```

**Purpose:** Create a second account to act as a buyer

---

### Step 5: View Available Players for Sale

**GET** `/api/transfer-listings/`
**Headers:** `Authorization: Bearer <buyer_access_token>`

**Response:**
```json
[
  {
    "id": 1,  // ← Use this listing_id to buy
    "player": {
      "id": 1,
      "name": "Player_GK_YXUC7L",
      "position": "GK",
      "value": "1000000.00"
    },
    "asking_price": "1500000.00",
    "is_active": true
  }
]
```

**Purpose:** See all players currently for sale. Copy the `id` (listing_id) to buy.

---

### Step 6: Buy a Player

**POST** `/api/transfer-listings/{listing_id}/buy/`
**Headers:** `Authorization: Bearer <buyer_access_token>`

Replace `{listing_id}` with the ID from Step 5 (e.g., use `1` if `id: 1`)

**Response:**
```json
{
  "message": "Player purchased successfully",
  "transaction": {
    "id": 1,
    "buyer": {"username": "user2"},
    "seller": {"username": "user1"},
    "player": {"name": "Player_GK_YXUC7L"},
    "transfer_amount": "1500000.00"
  }
}
```

**What happens:**
- Buyer pays the asking price
- Seller receives the money
- Player transfers to buyer's team
- Player value increases by 5-15% randomly
- Transaction record is created

**Important:** Cannot buy your own player (will return 400 error)

---

### Step 7: View Transaction History

**GET** `/api/transactions/?my_transactions=true`
**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
[
  {
    "id": 1,
    "buyer": {"username": "user2"},
    "seller": {"username": "user1"},
    "player": {"name": "Player_GK_YXUC7L"},
    "transfer_amount": "1500000.00",
    "created_at": "2025-10-27T08:30:00Z"
  }
]
```

**Purpose:** View all your completed transfers (as buyer or seller)

---

### Additional Useful Endpoints

#### Login to Get New Tokens
**POST** `/api/token/`
```json
{
  "username": "user1",
  "password": "SecurePass123"
}
```
Returns fresh access and refresh tokens.

#### Refresh Access Token
**POST** `/api/token/refresh/`
```json
{
  "refresh": "<refresh_token>"
}
```

#### View All Players in System
**GET** `/api/players/`
Shows all players across all teams.

#### View Your Players Only
**GET** `/api/players/my-players/`
Shows only players in your team.

#### Cancel Your Listing
**POST** `/api/transfer-listings/{listing_id}/cancel/`
Remove your player from the market before someone buys.

---

## Key Concepts

### listing_id vs player_id
- **player_id**: ID of the player (e.g., Player 1, Player 2)
- **listing_id**: ID of the transfer listing created when listing a player for sale
- When buying: Use **listing_id** (not player_id)

### Authentication
- Most endpoints require JWT token in header: `Authorization: Bearer <access_token>`
- Token expires after 24 hours
- Use refresh token to get new access token

### Capital Management
- Teams start with $5,000,000
- Cannot modify capital directly via API
- Capital transfers automatically during purchases

### Player Values
- Start at $1,000,000 each
- Increase 5-15% after each transfer
- Cannot modify values directly via API

---

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## API Documentation

- **Postman Collection**: `Fantasy_Football_API.postman_collection.json`

## License

This project is part of a technical assessment and demonstration.
