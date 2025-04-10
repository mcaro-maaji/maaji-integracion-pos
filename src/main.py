"""Modulo de ejecucion principal"""

from web.routes import app

if __name__ == "__main__":
    app.run(debug=True)
