# File: components/cascading_selects/parent_select.py
from typing import Any, Dict
from django_components import component
from .states import states_countries_list

@component.register("parent_select_cascading_selects")
class ParentSelectCascadingSelectsComponent(component.Component):
    template = """
        <div>
            <label class="label">Country</label>
            <select id="country-select" class="input" name="country" hx-get="{% url 'select_cascading_selects' %}" hx-target="#states" hx-trigger="change">
                <option value="">Choose a country...</option>
                {% for country in countries %}
                    <option value="{{ country.name }}">{{ country.name }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mt-2">
            <label class="label">State</label>
            <select id="states" name="state" class="input">
                <!-- States will be populated based on selected country -->
            </select>
        </div>
    """

    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        countries = states_countries_list
        return {'countries': countries}
