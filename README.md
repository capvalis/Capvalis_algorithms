# Capvalis Algo Engine

A Flask-based algorithmic trading engine that supports multiple brokers including Fyers and Angel One.

## Features

- Multi-broker support (Fyers, Angel One)
- Web-based interface for broker connection
- Secure credential management
- Real-time market data processing
- Algorithmic trading execution

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/capvalis_algo_engine.git
cd capvalis_algo_engine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

## Usage

1. Start the Flask server:
```bash
flask run
```

2. Open your browser and navigate to `http://localhost:5000`

3. Select your broker and enter the required credentials

4. The system will validate your credentials and establish a connection

## Project Structure

```
capvalis_algo_engine/
├── app.py              # Flask application
├── broker_connect.py   # Broker connection handling
├── config.py           # Configuration management
├── requirements.txt    # Project dependencies
├── static/            # Static files (CSS, JS)
└── templates/         # HTML templates
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 