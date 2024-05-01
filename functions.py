from typing import List, Optional


import db_functions
from settings import ALIVE, FINISHED, STAGES


async def get_users_for_messages() -> List[Optional[db_functions.User]]:
    users_summary = []
    for stage in STAGES.values():
        users = await db_functions.get_users_to_notify(stage)
        users_summary += users

    return users_summary


async def set_status(stage_num) -> str:
    if stage_num == len(STAGES):
        status = FINISHED
    else:
        status = ALIVE
    
    return status
