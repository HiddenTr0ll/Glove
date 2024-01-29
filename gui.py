from settings import *
import settings


class GUI():
    def __init__(self):
        self.menuEnabled = False
        self.saveDialogEnabled = False
        self.saveMode = ""
        self.fileName = ""
        self.settings = {
            "debug": False,
            "saveDialog": False,
            "audioOn": False
        }

        self.active = {
            "window": False,
            "child": False,
            "tooltip": False,
            "menu bar": False,
            "popup": False,
            "popup modal": False,
            "popup context item": False,
            "popup context window": False,
            "drag drop": False,
            "group": False,
            "tab bar": False,
            "list box": False,
            "popup context void": False,
            "table": False,
        }

    def frame_commands(self):
        io = imgui.get_io()
        if settings.audioOn == False:
            self.settings["audioOn"] = False

        if self.saveDialogEnabled:
            imgui.open_popup("Save recorded "+self.saveMode+"s to file?")
            imgui.set_next_window_size(300, 100)
            with imgui.begin_popup_modal("Save recorded "+self.saveMode+"s to file?", flags=imgui.WINDOW_NO_RESIZE) as popup:
                if popup.opened:
                    imgui.text('Save as:')
                    imgui.same_line(spacing=10)
                    changed, self.fileName = imgui.input_text('',  self.fileName, flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL)

                    clicked_yes = imgui.button('Yes', width=50)
                    imgui.same_line(spacing=10)
                    clicked_no = imgui.button('No', width=50)

                    if clicked_yes:
                        if self.saveMode == "Key":
                            settings.recorder.saveKeyRecording(self.fileName)
                        else:
                            settings.recorder.saveMovementRecording(self.fileName)
                        self.saveDialogEnabled = False
                    if clicked_no:
                        self.saveDialogEnabled = False

        with imgui.begin_main_menu_bar() as main_menu_bar:
            if main_menu_bar.opened:
                with imgui.begin_menu("File", True) as file_menu:
                    if file_menu.opened:
                        clicked_quit, selected_quit = imgui.menu_item("Quit", "ALT + F4")
                        if clicked_quit:
                            settings.running = False
                with imgui.begin_menu("Record", True) as recording_menu:
                    if recording_menu.opened:
                        if not settings.recorder.recordingKeys:
                            clickedRecordKeys, _ = imgui.menu_item("Start Key Recording", "F5")
                        else:
                            clickedRecordKeys, _ = imgui.menu_item("Stop Key Recording", "F5")
                        if clickedRecordKeys:
                            if not settings.recorder.recordingKeys:
                                settings.recorder.startKeyRecording()
                            else:
                                settings.recorder.stopKeyRecording()
                                self.saveDialog("Key")

                        if not settings.recorder.recordingMovement:
                            clickedRecordMovement, _ = imgui.menu_item("Start Movement Recording", "F6")
                        else:
                            clickedRecordMovement, _ = imgui.menu_item("Stop Movement Recording", "F6")
                        if clickedRecordMovement:
                            if not settings.recorder.recordingMovement:
                                settings.recorder.startMovementRecording()
                            else:
                                settings.recorder.stopMovementRecording()
                                self.saveDialog("Movement")

                with imgui.begin_menu("Settings", True) as settings_menu:
                    if settings_menu.opened:
                        for label, enabled in self.settings.copy().items():
                            clicked, enabled = imgui.checkbox(label, enabled)
                            self.settings[label] = enabled
                            if label == "audioOn":
                                if enabled:
                                    settings.audioOn = True
                        changed, values = imgui.drag_float2("Movementspeed Horizontal, Vertical", settings.movementSpeedH,
                                                            settings.movementSpeedV, change_speed=0.01, min_value=0.1, max_value=2, format="%.1f")
                        if changed:
                            settings.movementSpeedH = values[0]
                            settings.movementSpeedV = values[1]

                        changed, values = imgui.drag_float("Mouse Sensitivity", settings.mouseSensitivity, change_speed=0.01, min_value=0.1, max_value=2, format="%.1f")
                        if changed:
                            settings.mouseSensitivity = values

        if self.settings["debug"]:

            with imgui.begin("Debug", flags=(imgui.WINDOW_ALWAYS_AUTO_RESIZE+imgui.WINDOW_NO_COLLAPSE)):
                imgui.text("Framerate: " + str(settings.framerate) + " FPS")
                imgui.text("CamPos: " + np.array2string(settings.camPos, precision=2))
                imgui.text("CamTheta: " + str(settings.camTheta))
                imgui.text("CamPhi: " + str(settings.camPhi))

        # turn examples on/off
        with imgui.begin("self.active examples"):
            for label, enabled in self.active.copy().items():
                _, enabled = imgui.checkbox(label, enabled)
                self.active[label] = enabled

        if self.active["window"]:
            with imgui.begin("Hello, Imgui!"):
                imgui.text("Hello, World!")

        if self.active["child"]:
            with imgui.begin("Example: child region"):
                with imgui.begin_child("region", 150, -50, border=True):
                    imgui.text("inside region")
                imgui.text("outside region")

        if self.active["tooltip"]:
            with imgui.begin("Example: tooltip"):
                imgui.button("Click me!")
                if imgui.is_item_hovered():
                    with imgui.begin_tooltip():
                        imgui.text("This button is clickable.")

        if self.active["menu bar"]:
            try:
                flags = imgui.WINDOW_MENU_BAR
                with imgui.begin("Child Window - File Browser", flags=flags):
                    with imgui.begin_menu_bar() as menu_bar:
                        if menu_bar.opened:
                            with imgui.begin_menu('File') as file_menu:
                                if file_menu.opened:
                                    clicked, state = imgui.menu_item('Close')
                                    if clicked:
                                        self.active["menu bar"] = False
                                        raise Exception
            except Exception:
                print("exception handled")

        if self.active["popup"]:
            with imgui.begin("Example: simple popup"):
                if imgui.button("select"):
                    imgui.open_popup("select-popup")
                imgui.same_line()
                with imgui.begin_popup("select-popup") as popup:
                    if popup.opened:
                        imgui.text("Select one")
                        imgui.separator()
                        imgui.selectable("One")
                        imgui.selectable("Two")
                        imgui.selectable("Three")

        if self.active["popup modal"]:
            with imgui.begin("Example: simple popup modal"):
                if imgui.button("Open Modal popup"):
                    imgui.open_popup("select-popup-modal")
                imgui.same_line()
                with imgui.begin_popup_modal("select-popup-modal") as popup:
                    if popup.opened:
                        imgui.text("Select an option:")
                        imgui.separator()
                        imgui.selectable("One")
                        imgui.selectable("Two")
                        imgui.selectable("Three")

        if self.active["popup context item"]:
            with imgui.begin("Example: popup context view"):
                imgui.text("Right-click to set value.")
                with imgui.begin_popup_context_item("Item Context Menu") as popup:
                    if popup.opened:
                        imgui.selectable("Set to Zero")

        if self.active["popup context window"]:
            with imgui.begin("Example: popup context window"):
                with imgui.begin_popup_context_window() as popup:
                    if popup.opened:
                        imgui.selectable("Clear")

        if self.active["popup context void"]:
            with imgui.begin_popup_context_void() as popup:
                if popup.opened:
                    imgui.selectable("Clear")

        if self.active["drag drop"]:
            with imgui.begin("Example: drag and drop"):
                imgui.button('source')
                with imgui.begin_drag_drop_source() as src:
                    if src.dragging:
                        imgui.set_drag_drop_payload('itemtype', b'payload')
                        imgui.button('dragged source')
                imgui.button('dest')
                with imgui.begin_drag_drop_target() as dst:
                    if dst.hovered:
                        payload = imgui.accept_drag_drop_payload('itemtype')
                        if payload is not None:
                            print('Received:', payload)

        if self.active["group"]:
            with imgui.begin("Example: item groups"):
                with imgui.begin_group():
                    imgui.text("First group (buttons):")
                    imgui.button("Button A")
                    imgui.button("Button B")
                imgui.same_line(spacing=50)
                with imgui.begin_group():
                    imgui.text("Second group (text and bullet texts):")
                    imgui.bullet_text("Bullet A")
                    imgui.bullet_text("Bullet B")

        if self.active["tab bar"]:
            with imgui.begin("Example Tab Bar"):
                with imgui.begin_tab_bar("MyTabBar") as tab_bar:
                    if tab_bar.opened:
                        with imgui.begin_tab_item("Item 1") as item1:
                            if item1.opened:
                                imgui.text("Here is the tab content!")
                        with imgui.begin_tab_item("Item 2") as item2:
                            if item2.opened:
                                imgui.text("Another content...")
                        global opened_state
                        with imgui.begin_tab_item("Item 3") as item3:
                            opened_state = item3.opened
                            if item3.selected:
                                imgui.text("Hello Saylor!")

        if self.active["list box"]:
            with imgui.begin("Example: custom listbox"):
                with imgui.begin_list_box("List", 200, 100) as list_box:
                    if list_box.opened:
                        imgui.selectable("Selected", True)
                        imgui.selectable("Not Selected", False)

        if self.active["table"]:
            with imgui.begin("Example: table"):
                with imgui.begin_table("data", 2) as table:
                    if table.opened:
                        imgui.table_next_column()
                        imgui.table_header("A")
                        imgui.table_next_column()
                        imgui.table_header("B")

                        imgui.table_next_row()
                        imgui.table_next_column()
                        imgui.text("123")

                        imgui.table_next_column()
                        imgui.text("456")

                        imgui.table_next_row()
                        imgui.table_next_column()
                        imgui.text("789")

                        imgui.table_next_column()
                        imgui.text("111")

                        imgui.table_next_row()
                        imgui.table_next_column()
                        imgui.text("222")

                        imgui.table_next_column()
                        imgui.text("333")

    def saveDialog(self, mode):
        if mode == "Movement" and settings.recorder.movementCount == 0:
            print("recording aborted or no data available")
        if mode == "Key" and settings.recorder.keyCount == 0:
            print("recording aborted or no data available")
        else:
            self.saveDialogEnabled = True
            self.saveMode = mode
            self.fileName = "New"+mode+"File"

    def render(self):
        settings.impl.process_inputs()
        imgui.new_frame()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if settings.font is not None:
            imgui.push_font(settings.font)
        self.frame_commands()

        if settings.font is not None:
            imgui.pop_font()

        imgui.render()
