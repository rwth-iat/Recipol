# src/frontend/Workers.py
from PyQt6.QtCore import QThread, pyqtSignal

# from Code.Recipol.mtpparser import getMtps
# from Code.Recipol.orchestration import getProcedure
from backend import getMtps, getProcedure


class Worker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, mtp_files, recipe_files=None):
        super().__init__()
        self.files = mtp_files  # Absolute .aml file path list selected in UI
        self.total_mtp_files = len(mtp_files)
        self.recipe_files = recipe_files or []  # Absolute .xml recipe file path list
        self.mtp_results = []
        self.failed_files = []
        self.sfc_results = []
        self.failed_recipe_files = []

    def run(self):
        self.mtp_results = []
        self.failed_files = []
        self.sfc_results = []
        self.failed_recipe_files = []
        total_files = len(self.files)
        success_files = 0

        if total_files > 0:
            self.log_signal.emit("Starting batch processing of MTP tasks...")

            for idx, file in enumerate(self.files, start=1):
                try:
                    self.log_signal.emit(f"Processing ({idx}/{total_files}): {file}")
                    parsed = getMtps(input_files=[file], logger=self.log_signal.emit)

                    if parsed:
                        # Count one file as success when at least one module is parsed.
                        self.mtp_results.extend(parsed)
                        success_files += 1
                        self.log_signal.emit(f"Success: {file}")
                    else:
                        self.failed_files.append(file)
                        self.log_signal.emit(f"No valid MTP data parsed from: {file}")
                except Exception as e:
                    self.failed_files.append(file)
                    self.log_signal.emit(f"Failed to process {file}: {str(e)}")

                # Progress is based on successful files only.
                self.progress_signal.emit(int(success_files / total_files * 100))

            if self.failed_files:
                self.log_signal.emit(
                    f"Completed with issues: {success_files}/{total_files} files succeeded, "
                    f"{len(self.failed_files)} failed."
                )
            else:
                self.log_signal.emit(f"Completed: all {total_files} files succeeded.")
        else:
            # No MTP files selected: keep progress complete for recipe-only view.
            self.progress_signal.emit(100)
            self.log_signal.emit("No MTP files selected. Skipping MTP parsing.")

        if self.recipe_files:
            self.log_signal.emit("Generating SFC from selected Recipe file(s)...")
            for recipe in self.recipe_files:
                try:
                    rows = getProcedure(
                        recipe_files=[recipe],
                        mtp_files=self.files,
                        logger=self.log_signal.emit,
                    )
                    if rows:
                        self.sfc_results.extend(rows)
                    else:
                        self.failed_recipe_files.append(recipe)
                        self.log_signal.emit(f"No SFC data generated from: {recipe}")
                except Exception as e:
                    self.failed_recipe_files.append(recipe)
                    self.log_signal.emit(f"Failed to generate SFC from {recipe}: {str(e)}")

        self.log_signal.emit(f"Task completed. Parsed {len(self.mtp_results)} modules in total.")
        self.finished_signal.emit()
