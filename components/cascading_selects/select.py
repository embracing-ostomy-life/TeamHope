from django_components import component

from .states import state_countries_dict

@component.register("select_cascading_selects")
class SelectCascadingSelectsComponent(component.Component):
    template = """
        {% for state in states %}
            <option value="{{ state }}">{{ state }}</option>
        {% endfor %}
    """

    def get_context_data(self, country, *args, **kwargs):
        states = state_countries_dict.get(country)
        print(country)
        return {'states' : state_countries_dict.get(country)}

    def get(self, request, *args, **kwargs):
        country = request.GET.get("country")
        states = state_countries_dict[country]
        return self.render_to_response({"states": states})
