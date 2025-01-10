from flask import request
import user_agents


def get_user_agent(r: request):
    user_agent = r.headers.get('User-Agent')
    return user_agents.parse(user_agent)
