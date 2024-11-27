// Real-time Data API URLs
const API_BASE_URL = "https://api.coingecko.com/api/v3/";
const FEAR_GREED_INDEX_URL = "https://api.alternative.me/fng/";

// Stock Data API (Example: Alpha Vantage or Yahoo Finance)
// You would need your own API key for these services. Here's an example for Alpha Vantage.
const STOCK_API_URL = "https://www.alphavantage.co/query";
const ALPHA_VANTAGE_API_KEY = "3FVTJ1BXCBM6DNVF";  // Replace with your Alpha Vantage API key

// DOM Elements for Crypto
const marketCapEl = document.getElementById("market-cap");
const volumeEl = document.getElementById("volume");
const dominanceEl = document.getElementById("dominance");
const fearGreedEl = document.getElementById("fear-greed");
const btcTile = document.getElementById("btc-tile");
const ethTile = document.getElementById("eth-tile");
const selectedCoinEl = document.getElementById("selected-coin");

// DOM Elements for Stocks
const marketCapStocksEl = document.getElementById("market-cap-stocks");
const volumeStocksEl = document.getElementById("volume-stocks");
const dominanceStocksEl = document.getElementById("dominance-stocks");
const ndaqTile = document.getElementById("ndaq-tile");
const nvdiaTile = document.getElementById("nvdia-tile");
const appleTile = document.getElementById("apple-tile");
const selectedStockEl = document.getElementById("selected-stock");

// Show crypto or stocks section based on the selected tab
const cryptoSection = document.getElementById("crypto-section");
const stocksSection = document.getElementById("stocks-section");

const cryptoSlide = document.getElementById("crypto-slide");
const stocksSlide = document.getElementById("stocks-slide");

cryptoSlide.addEventListener("click", () => {
  cryptoSection.style.display = "block";
  stocksSection.style.display = "none";
  cryptoSlide.classList.add("active");
  stocksSlide.classList.remove("active");
});

stocksSlide.addEventListener("click", () => {
  cryptoSection.style.display = "none";
  stocksSection.style.display = "block";
  stocksSlide.classList.add("active");
  cryptoSlide.classList.remove("active");
});

// Fetch Market Data (Crypto)
async function fetchMarketData() {
  try {
    const response = await fetch(`${API_BASE_URL}global`);
    const data = await response.json();

    marketCapEl.textContent = `Market Cap: $${(data.data.total_market_cap.usd / 1e9).toFixed(2)}B`;
    volumeEl.textContent = `24H Volume: $${(data.data.total_volume.usd / 1e9).toFixed(2)}B`;
    dominanceEl.textContent = `BTC Dominance: ${data.data.market_cap_percentage.btc.toFixed(1)}%`;
  } catch (error) {
    console.error("Error fetching market data:", error);
  }
}

// Fetch Fear & Greed Index (Crypto)
async function fetchFearGreedIndex() {
  try {
    const response = await fetch(FEAR_GREED_INDEX_URL);
    const data = await response.json();
    fearGreedEl.textContent = `Fear & Greed: ${data.data[0].value_classification}`;
  } catch (error) {
    console.error("Error fetching fear & greed index:", error);
  }
}

// Fetch Stock Data (NASDAQ, NVIDIA, Apple)
async function fetchStockData(symbol) {
  try {
    const response = await fetch(`${STOCK_API_URL}?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${ALPHA_VANTAGE_API_KEY}`);
    const data = await response.json();

    // Extract stock data from the response
    const stockData = data["Global Quote"];
    
    const marketCap = stockData["Market Capitalization"];
    const volume = stockData["24. volume"];
    const price = stockData["05. price"];

    marketCapStocksEl.textContent = `Market Cap: $${marketCap}`;
    volumeStocksEl.textContent = `24H Volume: ${volume}`;
    dominanceStocksEl.textContent = `Price: $${price}`;
  } catch (error) {
    console.error("Error fetching stock data:", error);
  }
}

// Load TradingView Widget (For both Crypto and Stocks)
function loadTradingViewWidget(symbol, isStock = false) {
  const containerId = isStock 
    ? "tradingview-widget-container-stocks" 
    : "tradingview-widget-container-crypto";
  
  const container = document.getElementById(containerId);
  container.innerHTML = "";  // Clear previous widget

  new TradingView.widget({
    container_id: containerId,
    symbol: symbol,
    interval: "D",
    timezone: "Etc/UTC",
    theme: "dark",
    style: "1", // Candle chart style
    locale: "en",
    toolbar_bg: "#f1f3f6",
    enable_publishing: false,
    hide_top_toolbar: false,
    allow_symbol_change: false,
    width: "100%", // Responsive width
    height: "400", // Adjust the height if necessary
  });
}

// Event Listeners for Coin Selection (Crypto)
btcTile.addEventListener("click", () => {
  loadTradingViewWidget("BINANCE:BTCUSDT");
  selectedCoinEl.textContent = "Interactive Price Chart for Bitcoin (BTC)";
});

ethTile.addEventListener("click", () => {
  loadTradingViewWidget("BINANCE:ETHUSDT");
  selectedCoinEl.textContent = "Interactive Price Chart for Ethereum (ETH)";
});

// Event Listeners for Stock Selection
ndaqTile.addEventListener("click", () => {
  loadTradingViewWidget("NASDAQ:NDX", true);
  selectedStockEl.textContent = "Interactive Price Chart for NASDAQ (NDX)";
  fetchStockData("NDX");
});

nvdiaTile.addEventListener("click", () => {
  loadTradingViewWidget("NASDAQ:NVDA", true);
  selectedStockEl.textContent = "Interactive Price Chart for NVIDIA (NVDA)";
  fetchStockData("NVDA");
});

appleTile.addEventListener("click", () => {
  loadTradingViewWidget("NASDAQ:AAPL", true);
  selectedStockEl.textContent = "Interactive Price Chart for Apple (AAPL)";
  fetchStockData("AAPL");
});

// Initial Data Load
fetchMarketData();
fetchFearGreedIndex();
fetchStockData("NDX");  // Default to NASDAQ data
loadTradingViewWidget("BINANCE:BTCUSDT");  // Default to Bitcoin chart for Crypto
