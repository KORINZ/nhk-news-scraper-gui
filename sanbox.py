import customtkinter as ctk
import os
import sys
import time
from PIL import Image

from playground import set_tesseract_path, select_region_and_capture, ocr_image


# TODO: main frame: take screenshot, import image, settings (language, parameters, shortcuts, etc.)
# TODO: screenshot on release checkbox
# TODO: tab1: screenshot and ocr image with scroll bar
# TODO: tab2: imported image and ocr image with scroll bar
# TODO: tab3: text result box


class Tab(ctk.CTkTabview):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.input_image = None
        self.output_image = None

        self.add("Tab 1")
        self.tab_1 = ctk.CTkScrollableFrame(master=self.tab("Tab 1"))
        self.tab_1.pack(fill="both", expand=True)

        self.input_image_text = ctk.CTkLabel(self.tab_1, text="")
        self.input_image_text.grid(row=0, column=0, padx=20, pady=10)
        self.input_image_label = ctk.CTkLabel(
            self.tab_1, text="", image=self.input_image)
        self.input_image_label.grid(
            row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.output_image_text = ctk.CTkLabel(
            self.tab_1, text="")
        self.output_image_text.grid(row=2, column=0, padx=20, pady=10)
        self.output_image_label = ctk.CTkLabel(
            self.tab_1, text="", image=self.output_image)
        self.output_image_label.grid(
            row=3, column=0, padx=20, pady=10, sticky="nsew")

        # Configure row and column weights
        self.tab_1.grid_rowconfigure(3, weight=1)
        self.tab_1.grid_columnconfigure(0, weight=1)

        self.add("Tab 2")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("image_example.py")
        self.geometry("800x800")
        self.image_scale_factor = 1

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.take_screenshot_button = ctk.CTkButton(
            self, text="Take Screenshot", command=self.take_screen_shot)
        self.take_screenshot_button.grid(
            row=0, column=0, padx=20, pady=10)

        self.tabview = Tab(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "ocr_images")

    def take_screen_shot(self) -> None:

        # Minimize window when pressing the button
        self.iconify()
        time.sleep(0.5)

        try:
            set_tesseract_path()
        except (RuntimeError, FileNotFoundError) as e:
            print(e)
            sys.exit(1)
        coords = {"ix": -1, "iy": -1, "x_end": -
                  1, "y_end": -1, "drawing": False}
        screenshot_region = select_region_and_capture(coords)
        result = ocr_image(
            screenshot_region,
            preprocess_params={
                "size": (screenshot_region.width * 4, screenshot_region.height * 4)
            },
        )
        print(result)

        screenshot_image = Image.frombytes(
            "RGB", (screenshot_region.width, screenshot_region.height), screenshot_region.tobytes())

        image_size = (int(screenshot_region.width * self.image_scale_factor),
                      int(screenshot_region.height * self.image_scale_factor))

        self.input_image = ctk.CTkImage(screenshot_image, size=(
            image_size[0], image_size[1]))
        self.tabview.input_image_label.configure(image=self.input_image)

        processed_image = Image.open(
            os.path.join(self.image_path, "preprocessed.png"))
        self.output_image = ctk.CTkImage(processed_image, size=(
            image_size[0], image_size[1]))
        self.tabview.output_image_label.configure(image=self.output_image)

        self.tabview.input_image_text.configure(
            text=f"Input Image")
        self.tabview.output_image_text.configure(
            text=f"Output Image")

        # Maximize window when done
        self.deiconify()


if __name__ == "__main__":
    app = App()
    app.mainloop()
