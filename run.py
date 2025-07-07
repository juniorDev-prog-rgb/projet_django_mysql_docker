from app import create_app, socketio
import os

app = create_app()

if __name__ == "__main__":
    # Configuration pour Docker
    debug = os.environ.get('FLASK_ENV') == 'development'
    host = '0.0.0.0'  # Important pour Docker
    port = int(os.environ.get('PORT', 5000))
    
    # Utiliser socketio.run pour supporter WebSocket
    socketio.run(app, debug=debug, host=host, port=port)
