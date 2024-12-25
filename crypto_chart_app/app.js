const chartContainer = document.getElementById('chart-container');
const cryptoInput = document.getElementById('crypto');
const intervalInput = document.getElementById('interval');
const fetchButton = document.getElementById('fetch-button');

const chart = LightweightCharts.createChart(chartContainer, {
    width: 800,
    height: 400,
    layout: {
        backgroundColor: '#ffffff',
        textColor: '#333333',
    },
    grid: {
        vertLines: {
            color: '#e5e5e5',
        },
        horzLines: {
            color: '#e5e5e5',
        },
    },
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
    },
    timeScale: {
        timeVisible: true,
        secondsVisible: false,
    },
});

const candlestickSeries = chart.addCandlestickSeries();

async function fetchHistoricalData(crypto, interval) {
    const limit = 100; // Number of data points to fetch
    const apiUrl = `https://api.binance.com/api/v3/klines?symbol=${crypto}&interval=${interval}&limit=${limit}`;

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        const formattedData = data.map(d => ({
            time: d[0] / 1000,
            open: parseFloat(d[1]),
            high: parseFloat(d[2]),
            low: parseFloat(d[3]),
            close: parseFloat(d[4]),
        }));
        return formattedData;
    } catch (error) {
        console.error('Error fetching historical data:', error);
        return [];
    }
}

async function updateChart(crypto, interval) {
    const historicalData = await fetchHistoricalData(crypto, interval);
    candlestickSeries.setData(historicalData);

    setInterval(async () => {
        const newData = await fetchHistoricalData(crypto, interval);
        if (newData.length > 0) {
            const lastCandle = newData[newData.length - 1];
            candlestickSeries.update(lastCandle);
        }
    }, 3000);
}

fetchButton.addEventListener('click', () => {
    const crypto = cryptoInput.value.toUpperCase();
    const interval = intervalInput.value;
    updateChart(crypto, interval);
});

// Initial chart update
updateChart('BTCUSDT', '1h');
