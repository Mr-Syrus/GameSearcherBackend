import re

import config

def init():
    app = config.APP

    # app.include_router(
    #     v1.init(),
    #     responses={
    #         401: {"detail": "Invalid token"},
    #         500: {"detail": "Internal Server Error"}
    #     }
    # )
