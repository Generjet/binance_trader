import React, { useEffect, useState } from 'react';
import socketIOClient from 'socket.io-client';

const ENDPOINT = "http://localhost:5000";

const CryptoDashboard = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const socket = socketIOClient(ENDPOINT);
    socket.on('update_data', (newData) => {
      setData((prevData) => [...prevData, ...newData]);
    });

    socket.emit('start_analysis', { symbol: 'ETHUSDT', timePeriod: '1h', lookback: 30 });

    return () => socket.disconnect();
  }, []);

  return (
    <div>
      <h1>Crypto Trading Dashboard</h1>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>Volume</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>{row.Time}</td>
              <td>{row.Open}</td>
              <td>{row.High}</td>
              <td>{row.Low}</td>
              <td>{row.Close}</td>
              <td>{row.Volume}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CryptoDashboard;