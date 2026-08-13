import { useCallback, useEffect, useState } from "react";
import {
  buyInOneClick,
  formatPrice,
  getProducts,
  CURRENCY_LABELS,
} from "./api/products.js";
import ProductCard from "./components/ProductCard.jsx";
import BuyInOneClickModal from "./components/BuyInOneClickModal.jsx";
import PaymentPage from "./components/PaymentPage.jsx";

const CURRENCIES = ["usd", "rub", "eur"];

export default function App() {
  const [currency, setCurrency] = useState("usd");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [buyProduct, setBuyProduct] = useState(null);
  const [payment, setPayment] = useState(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);
    getProducts(currency)
      .then((result) => {
        if (!cancelled) setProducts(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [currency]);

  const handleBuyOneClick = useCallback(
    async (productId, productPriceId, cur, price) => {
      const result = await buyInOneClick(productId, productPriceId, cur);
      if (!result.client_secret) {
        throw new Error("Сервер не вернул client_secret");
      }
      const selected = buyProduct;
      setBuyProduct(null);
      setPayment({
        clientSecret: result.client_secret,
        product: {
          name: selected?.name ?? "",
          priceLabel: price ? formatPrice(price.price, price.currency) : null,
        },
      });
    },
    [buyProduct]
  );

  if (payment) {
    return (
      <PaymentPage
        clientSecret={payment.clientSecret}
        product={payment.product}
        onBack={() => setPayment(null)}
      />
    );
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Товары</h1>
        <div className="app__currencies">
          {CURRENCIES.map((cur) => (
            <button
              key={cur}
              type="button"
              className="app__currency"
              data-active={currency === cur}
              onClick={() => setCurrency(cur)}
            >
              {CURRENCY_LABELS[cur]}
            </button>
          ))}
        </div>
      </header>

      {loading && <p className="app__status">Загрузка…</p>}
      {error && <p className="app__status app__status--error">Ошибка: {error}</p>}

      {!loading && !error && products.length === 0 && (
        <p className="app__status">Нет товаров</p>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="app__grid">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onBuyOneClick={(p) => setBuyProduct(p)}
            />
          ))}
        </div>
      )}

      {buyProduct && (
        <BuyInOneClickModal
          product={buyProduct}
          onClose={() => setBuyProduct(null)}
          onSubmit={handleBuyOneClick}
        />
      )}
    </div>
  );
}
