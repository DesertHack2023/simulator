import logging
from dataclasses import fields

from dearpygui import dearpygui as dpg

logger = logging.getLogger("GUI.ParameterSelector")


def update_variable(label, variable, sender, app_data, user_data):
    variable = app_data
    logger.debug(
        f"Sender: {sender}, app_data: {app_data}, user_data: {user_data}. {label} changed to {variable}"
    )


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

                    def wrapper(label, variable):
                        def func(sender, app_data, user_data):
                            update_variable(
                                label, variable, sender, app_data, user_data
                            )

                        return func

                    match variable:
                        case int():
                            dpg.add_input_int(
                                parent=node,
                                default_value=variable,
                                label=label,
                                callback=wrapper(label, variable),
                            )
                        case float():
                            dpg.add_input_float(
                                parent=node,
                                default_value=variable,
                                label=label,
                                callback=wrapper(label, variable),
                            )
                        case _:
                            dpg.add_text("haven't done this type yet")
