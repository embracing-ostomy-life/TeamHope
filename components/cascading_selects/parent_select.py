from typing import Any, Dict
from django_components import component

from .states import states_countries_list

@component.register("parent_select_cascading_selects")
class ParentSelectCascadingSelectsComponent(component.Component):
    template = """
        <div>
            <label class="label">Country</label>
            <select class="input" name="country" hx-get="{% url 'select_cascading_selects' %}" hx-target="#states">
            {% for country in countries %}
                <option value="{{ country.name }}">{{ country.name }}</option>
            {% endfor %}
            </select>
        </div>
        <div class="mt-2">
            <label class="label">State</label>
            <select id="states" name="state" class="input">
                {% component "select_cascading_selects" country='United States'%}{% endcomponent %}
            </select>
        </div>
    """


    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        countries = states_countries_list
        return {'countries' : countries}
