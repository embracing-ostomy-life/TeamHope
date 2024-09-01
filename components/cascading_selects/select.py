# File: components/cascading_selects/select.py
from typing import Any, Dict
from django_components import component
from .states import state_countries_dict

@component.register("select_cascading_selects")
class SelectCascadingSelectsComponent(component.Component):
    template = """
        {% for state in states %}
            <option value="{{ state }}">{{ state }}</option>
        {% endfor %}
    """

    

    def get(self, request, *args, **kwargs):
        country = request.GET.get("country")
        print("COUNTRY " + country)
        if not country:
            return self.render_to_response({"states": []})
        states = state_countries_dict.get(country, [])
        return self.render_to_response({"states": states})
        # country = request.GET.get("country")
        # if not country:
        #     raise ValueError("Country parameter is required for the request.")
        # states = state_countries_dict
        # return self.render_to_response({"states": states})
