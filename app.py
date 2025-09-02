import logging

import uvicorn

import config
import incelization

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")
