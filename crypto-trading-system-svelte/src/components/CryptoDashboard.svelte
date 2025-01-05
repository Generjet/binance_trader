<script>
    import { onMount } from 'svelte';
    import io from 'socket.io-client';
  
    let data = [];
    const ENDPOINT = "http://localhost:5000";
  
    onMount(() => {
      const socket = io(ENDPOINT);
  
      socket.on('update_data', (newData) => {
        data = [...data, ...newData];
      });
  
      socket.emit('start_analysis', { symbol: 'ETHUSDT', timePeriod: '1h', lookback: 30 });
  
      return () => socket.disconnect();
    });
  </script>
  
  <style>
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      border: 1px solid #ddd;
      padding: 8px;
    }
    th {
      background-color: #f2f2f2;
    }
  </style>
  
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
        {#each data as row}
          <tr>
            <td>{row.Time}</td>
            <td>{row.Open}</td>
            <td>{row.High}</td>
            <td>{row.Low}</td>
            <td>{row.Close}</td>
            <td>{row.Volume}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>