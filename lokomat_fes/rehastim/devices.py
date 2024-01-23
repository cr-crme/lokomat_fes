from threading import Timer
from typing import override
from abc import ABC, abstractproperty, abstractmethod

from pyScienceMode import Channel, RehastimGeneric as pyScienceModeRehastimGeneric


class RehastimGeneric(ABC):
    """
    This device mechanism serves as a standardisation layer to account for discrepancies of the implementation of the
    devices in the pyScienceMode library.
    """

    def __init__(self, port: str, show_log: bool = False) -> None:
        self.port = port
        self.show_log = show_log

        self._device = self._get_initialized_device()
        self._is_stimulation_initialized = False
        self._channels_has_changed = True

    @abstractproperty
    def device_name(self) -> str:
        """Get the name of the device."""

    def start_stimulation(self, duration: float = None) -> None:
        """Perform a stimulation.

        Parameters
        ----------
        duration : float
            The duration of the stimulation in seconds. If None, the stimulation will be performed up to the call of
            [stop_stimulation].
        """

        if not self._is_stimulation_initialized:
            # On the very first call, we initialize the stimulation. This takes care of the channels at the same time.
            self._initialize_stimulation()
            self._channels_has_changed = False

        channels = None
        if self._channels_has_changed:
            channels = self.get_channels()

        self._device.start_stimulation(upd_list_channels=channels)
        if duration is not None:
            Timer(duration, self.stop_stimulation).start()

    def stop_stimulation(self) -> None:
        """Pause the stimulation."""

        self._device.pause_stimulation()

    def dispose(self) -> None:
        """Dispose the device."""
        self._device.end_stimulation()
        self._device.disconnect()
        self._device.close_port()

    @abstractmethod
    def _get_initialized_device(self) -> pyScienceModeRehastimGeneric:
        """Convert to a pyScienceMode device."""

    def initialize_stimulation(self) -> None:
        """Initialize the stimulation and the channels."""

        self._initialize_stimulation()
        self._is_stimulation_initialized = True
        self._channels_has_changed = False

    @abstractmethod
    def _initialize_stimulation(self, channels: list[Channel]) -> None:
        """Initialize the stimulation at device level."""

    def set_channels(self, channels: list[Channel]) -> None:
        """Set the channels."""

        self._set_channels(channels)
        self._channels_has_changed = True

    @abstractmethod
    def _set_channels(self, channels: list[Channel]) -> None:
        """Set the channels."""

    @abstractmethod
    def get_channels(self, low_frequency_factor: int) -> list[Channel]:
        """Initialize the channels."""


class Rehastim2(RehastimGeneric):
    def __init__(self, stimulation_interval: int, low_frequency_factor: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stimulation_interval = stimulation_interval
        self._low_frequency_factor = low_frequency_factor

    @override
    @property
    def device_name(self) -> str:
        return "Rehastim2"

    @override
    def _get_initialized_device(self) -> pyScienceModeRehastimGeneric:
        from pyScienceMode.devices.rehastim2 import Rehastim2 as pyScienceModeRehastim2

        return pyScienceModeRehastim2(port=self.port, show_log=self.show_log)

    @override
    def _initialize_stimulation(self) -> None:
        from pyScienceMode.devices.rehastim2 import Rehastim2 as pyScienceModeRehastim2

        self._device: pyScienceModeRehastim2
        self._device.init_channel(
            stimulation_interval=self._stimulation_interval,
            list_channels=self.get_channels(),
            low_frequency_factor=self._low_frequency_factor,
        )


class RehastimP24(RehastimGeneric):
    def __init__(self, port: str, show_log: bool = False) -> None:
        raise NotImplementedError("The RehastimP24Device is not implemented yet.")

    @override
    @property
    def device_name(self) -> str:
        return "RehastimP24"

    @override
    def _get_initialized_device(self) -> pyScienceModeRehastimGeneric:
        from pyScienceMode.devices.rehastimP24 import RehastimP24 as pyScienceModeRehastimP24

        return pyScienceModeRehastimP24(port=self.port, show_log=self.show_log)

    @override
    def _initialize_stimulation(self) -> None:
        from pyScienceMode.devices.rehastimP24 import RehastimP24 as pyScienceModeRehastimP24

        self._device: pyScienceModeRehastimP24
        self._device.init_stimulation(list_channels=self.get_channels())