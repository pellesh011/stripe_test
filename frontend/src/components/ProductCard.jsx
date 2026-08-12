import { useMemo, useState } from "react";
import { formatPrice } from "../api/products.js";

export default function ProductCard({ product }) {
  const price = product.prices?.[0] ?? null;
  const [message, setMessage] = useState(null);

  const priceLabel = useMemo(
    () => (price ? formatPrice(price.price, price.currency) : "—"),
    [price]
  );

  return (
    <div className="card">
      <h2 className="card__name">{product.name}</h2>
      <p className="card__price">{priceLabel}</p>
      <button
        type="button"
        className="card__buy"
        disabled={!price}
        onClick={() => {
          console.log("Купить:", product.name, priceLabel);
          setMessage(`Куплено: ${product.name} за ${priceLabel}`);
        }}
      >
        Купить
      </button>
      {message && (
        <p className="card__message" data-testid="buy-message">
          {message}
        </p>
      )}
    </div>
  );
}