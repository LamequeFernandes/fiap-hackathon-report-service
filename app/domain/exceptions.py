class ReportNotFoundError(Exception):
    def __init__(self, analysis_id: str) -> None:
        self.analysis_id = analysis_id
        super().__init__(f"Report for analysis {analysis_id} not found")


class ReportAlreadyExistsError(Exception):
    def __init__(self, analysis_id: str) -> None:
        self.analysis_id = analysis_id
        super().__init__(f"Report for analysis {analysis_id} already exists")
