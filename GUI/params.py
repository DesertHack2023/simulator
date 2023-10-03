import logging
from dataclasses import fields

from dearpygui import dearpygui as dpg

logger = logging.getLogger("GUI.ParameterSelector")


def update_variable(obj, attribute, sender, app_data, user_data):
    setattr(obj, attribute, app_data)
    logger.debug(f"{obj.__class__.__name__}.{attribute} changed to {app_data}")


class ParameterSelector:
    """
    creates a dynamic selection window, based on the Params class
    """

    def __init__(self, parent, params):
        self.parent = parent
        self.params = params
        self._render()

    def get_params(self):
        # this is meant to return a parameter object to be used by the simulator
        return self.params

    def _render(self):
        logger.debug("Rendering ParameterSelector")
        for field in fields(self.params):
            logger.debug(field)
            name = field.name.replace("_", " ").title()
            with dpg.tree_node(parent=self.parent, label=name) as node:
                parameter_group = getattr(self.params, field.name)
                logger.debug(parameter_group)
                for parameter_field in fields(parameter_group):
                    variable = getattr(parameter_group, parameter_field.name)
                    label = parameter_field.name.replace("_", " ").title()

                    def wrapper(obj, attribute):
                        def func(sender, app_data, user_data):
                            update_variable(obj, attribute, sender, app_data, user_data)

                        return func

                    match variable:
                        case int():
                            dpg.add_input_int(
                                parent=node,
                                default_value=variable,
                                label=label,
                                callback=wrapper(parameter_group, parameter_field.name),
                            )
                        case float():
                            dpg.add_input_float(
                                parent=node,
                                default_value=variable,
                                label=label,
                                callback=wrapper(parameter_group, parameter_field.name),
                            )
                        case _:
                            logger.debug("haven't done this type yet")
