# serial_instrument.py
import serial

COM_PORT = "COM4"  # Instrument port location
TIMEOUT = 1

class SerialInstrument:
    def __init__(self,
                 port: str,
                 timeout: float | None = 1,
                 **serial_kwargs) -> None:
        self._connection = serial.Serial(
            port=port,
            timeout=timeout,
            write_timeout=timeout,
            **serial_kwargs
        )
        idn = self.query("*IDN?")  # Query identification
        if idn:
            self._idn = idn
            print(f"Connected to {idn}.")
        else:
            self.disconnect()
            print("Serial Instrument could not be identified.")

    def write(self, command: str) -> None:
        command += "\n"  # Add termination
        self._connection.write(command.encode())

    def query(self, command: str) -> str:
        self.write(command)
        read_bytes = self._connection.readline()[:-1] # Remove newline
        return read_bytes.decode()
    
    def disconnect(self) -> None:
        self._connection.close()


if __name__ == "__main__":
    instrument = SerialInstrument(COM_PORT, TIMEOUT)
    instrument.disconnect()

    