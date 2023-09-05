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

        with dpg.table(
            parent="Primary Window", resizable=True, reorderable=True, hideable=True
        ):
            dpg.add_table_column(label="Logs")
            dpg.add_table_column(label="Parameters")
            with dpg.table_row():
                with dpg.child_window(height=350) as logger_window:
                    log = GUI.Logger(parent=logger_window)
                    log.setFormatter(formatter)
                    TimelapseLogger.addHandler(log)
                    GUI_Logger.addHandler(log)
                with dpg.child_window(height=350) as idk:
                    dpg.add_text("IDK Something", parent=idk)
            with dpg.table_row():
                with dpg.child_window() as parameters:
                    dpg.add_text(
                        "This is where the parameters will be set", parent=parameters
                    )
                with dpg.child_window() as no_idea:
                    dpg.add_text(
                        "IDK Something, the frames or something", parent=no_idea
                    )

    dpg.setup_dearpygui()
    dpg.set_primary_window("Primary Window", True)
    dpg.show_viewport(maximized=True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
