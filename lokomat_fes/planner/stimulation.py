from abc import ABC, abstractmethod
from typing import Callable, override

from ..common.data import Data
from .data_analyser import Side, DataAnalyser


class StimulationAbstract(ABC):
    @abstractmethod
    def stimulation_duration(self, current_time: float, data: Data) -> list[float | None]:
        """Check whether to stimulate at a given time.
        This method is called at every milliseconds.

        As long as this method returns None for a specific channel, nothing happens on this channel (meaning if it was
        stimulating, it keeps stimulating and if it was not stimulating, it keeps not stimulating).
        If it returns a positive value, the stimulation is started for this channel for the given duration in
        seconds. If it returns a negative value, the stimulation is stopped for this channel. If a 0 is sent, a
        stimulation is started, but never stopped (until a negative value is sent).

        Parameters
        ----------
        current_time : float
            The current time in seconds since t0.
        data : Data
            The current data

        Returns
        -------
        bool
            Whether to stimulate or not.
        """


class StrideBasedStimulation(StimulationAbstract):
    def __init__(self, condition_function: Callable[[float, float], tuple[bool, ...]]) -> None:
        """
        Parameters
        ----------
        condition_function: Callable[[float, float], tuple[bool, ...]]
            A function that takes the current stride position on left and right [0; 1]
            and returns a tuple of stimulation for each channels.
        """
        super(StrideBasedStimulation, self).__init__()
        self._condition = condition_function

        self._are_stimulating: list[bool] = []  # One per channel

    @override
    def stimulation_duration(self, current_time: float, data: Data) -> list[int | None]:
        # Get where we are in a stride cycle and whether we should stimulate or not channels
        stride_left = DataAnalyser.percentage_of_stride(current_time, data, Side.LEFT)
        stride_right = DataAnalyser.percentage_of_stride(current_time, data, Side.RIGHT)
        should_stimulate_channels = self._condition(stride_left, stride_right)
        if not self._are_stimulating:
            self._are_stimulating = [False] * len(should_stimulate_channels)

        # For each channel, check if we should start, stop, keep stimulating or keep not stimulating
        out = []
        for i in range(len(should_stimulate_channels)):
            should_stimulate = should_stimulate_channels[i]
            is_stimulating = self._are_stimulating[i]
            if should_stimulate and not is_stimulating:
                self._are_stimulating[i] = True
                out.append(0)
            elif should_stimulate and is_stimulating:
                out.append(None)
            elif not should_stimulate and is_stimulating:
                self._are_stimulating[i] = False
                out.append(-1)
            elif not should_stimulate and not is_stimulating:
                out.append(None)
            else:
                raise ValueError("This should never happen")

        return out


class TimeBasedStimulation(StimulationAbstract):
    def __init__(self, start_point: float, end_time: float) -> None:
        """
        Parameters
        ----------
        starting_point : float
            The starting point of the stimulation as a percentage of the stride [0; 1].
        end_time : float
            The end time of the stimulation in seconds.
        """
        super(TimeBasedStimulation, self).__init__()
        self._starting_point = start_point
        self._end_time = end_time

        self._stimulation_started_at = None

    @override
    def stimulation_duration(self, current_time: float, data: Data) -> list[int | None]:
        raise NotImplementedError("TODO")