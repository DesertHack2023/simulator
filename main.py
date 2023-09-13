import logging

import dearpygui.dearpygui as dpg

import GUI


def main():
    dpg.create_context()
    dpg.create_viewport(title="People Simulator")
    TimelapseLogger = logging.getLogger("Simulation")
    GUI_Logger = logging.getLogger("GUI")
    TimelapseLogger.setLevel(logging.DEBUG)
    GUI_Logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%H:%M:%S", style="{"
    )

    with dpg.window(tag="Primary Window"):
        with dpg.menu_bar():
            with dpg.menu(label="Tools"):
                dpg.add_menu_item(
                    label="Show Item Registry", callback=dpg.show_item_registry
                )
                dpg.add_menu_item(
                    label="Show Performance Metrics", callback=dpg.show_metrics
                )
                dpg.add_menu_item(label="Show Debug", callback=dpg.show_debug)

            with dpg.window(height=350, width=350, label="Logger") as logger_window:
                log = GUI.Logger(parent=logger_window)
                log.setFormatter(formatter)
                TimelapseLogger.addHandler(log)
                GUI_Logger.addHandler(log)
            with dpg.window(height=350, width=350, label="Parameters") as parameters:
                GUI.ParameterSelector(parent=parameters)
            with dpg.window(height=500, width=500, label="Canvas") as frame:
                GUI.Canvas(parent=frame, edges=[])

    dpg.setup_dearpygui()
    dpg.set_primary_window("Primary Window", True)
    dpg.show_viewport(maximized=True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
