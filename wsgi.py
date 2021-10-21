#!/usr/bin/env python3
from application import create_app

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True, load_dotenv=True, port=1334)
