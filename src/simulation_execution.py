from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict


ErronousElement = list | None


class SimulationExecution:
    """
    Represents a single teleoperation simulation run of robocasa. 
    """

    def __init__(
        self,
        scenario_data: Path,
    ) -> None:
        """
        Loads and validates simulation scenario data and evaluates execution success.
        :param scenario_data: path to scenario JSON file
        :type scenario_data: Path
        """
        self.__erronous_element: ErronousElement = None
        self.__scenario_data_path: Path = Path(scenario_data)
        self.__simulation_data: Dict[str, Any] = self.__load_scenario_data()
        self.__video_path: Path = self.__simulation_data["video_path"]

        self.__check()

    @property
    def simulation_data(self) -> Dict[str, Any]:
        return self.__simulation_data

    @property
    def video_path(self) -> Path:
        return self.__video_path

    @property
    def erronous_element(self) -> ErronousElement:
        return self.__erronous_element

    def was_successful(self) -> bool:
        return self.__erronous_element is None


    def __load_scenario_data(self) -> Dict[str, Any]:
        """
        Loads scenario JSON data from disk and validates its schema.

        :returns: parsed and validated scenario data
        :rtype: Dict[str, Any]
        :raises FileNotFoundError: if scenario file does not exist
        :raises ValueError: if required keys are missing
        :raises TypeError: if schema types are invalid
        """
        if not self.__scenario_data_path.exists():
            raise FileNotFoundError(
                f"Scenario data file not found: {self.__scenario_data_path}"
            )
        with self.__scenario_data_path.open("r", encoding="utf-8") as fh:
            data: Dict[str, Any] = json.load(fh)

        self.__validate_scenario_schema(data)
        return data

    @staticmethod
    def __validate_scenario_schema(data: Dict[str, Any]) -> None:
        """
        Validates that scenario JSON contains required structure and types.

        :param data: scenario dictionary to validate
        :type data: Dict[str, Any]
        :raises ValueError: if required keys are missing
        :raises TypeError: if atomic_tasks is not a dictionary
        """
        # simple validation
        required = {"composite_task", "completed", "hdf5_path", "video_path", "atomic_tasks"}
        missing = required - data.keys()
        if missing:
            raise ValueError(
                f"Scenario JSON is missing required keys: {missing}"
            )
        if not isinstance(data["atomic_tasks"], dict):
            raise TypeError(
                f"'atomic_tasks' must be a JSON object; "
                f"got {type(data['atomic_tasks']).__name__}."
            )

    def __check(self) -> None:
        """
        Evaluates simulation completion status and determines erroneous task if any.
        """
        if not self.__parse_bool(self.__simulation_data.get("completed", False)):
            self.__erronous_element = self.__locate_erroneous_task()
            return
 
        failed_task = self.__locate_erroneous_task()
        if failed_task is not None:
            self.__erronous_element = failed_task
 
    def __locate_erroneous_task(self) -> ErronousElement:
        """
        Finds the first atomic task that failed during simulation execution.

        :returns: task name and failure reason if found, otherwise None
        :rtype: ErronousElement
        """
        atomic_tasks: Dict[str, Any] = self.__simulation_data.get("atomic_tasks", {})
 
        for task_name, task_info in atomic_tasks.items():
            if not self.__parse_bool(task_info.get("completed", False)):
                reason: str = task_info.get("reason", "No reason provided.")
                return [task_name, reason]
        return None

    @staticmethod
    def __parse_bool(value: Any) -> bool:
        """
        Converts various input types into a boolean value.

        :param value: value to interpret as boolean
        :type value: Any
        :returns: normalized boolean interpretation
        :rtype: bool
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() == "true"
        return bool(value)

