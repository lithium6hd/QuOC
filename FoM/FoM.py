from abc import abstractmethod


class FoM:

    @abstractmethod
    def reset(self):
        """
        reset internal params.
        Returns
        -------
        """

    @abstractmethod
    def update(self, val: float) -> bool:
        """
        Update figure of merit.
        Returns
        -------
        Returns True if figure of merit is determined sufficiently, else False.
        """

    @abstractmethod
    def get(self) -> float:
        """
        Returns
        -------
        FoM
        """

    @abstractmethod
    def get_errror(self) -> float:
        """
        Returns
        -------
        Error of FoM
        """

    @abstractmethod
    def update_record(self) -> float:
        """
        Checks if new record.
        Returns
        -------
        Best FoM recorded.
        """