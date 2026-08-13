export const CURRENCY_LABELS = {
  usd: "USD",
  rub: "RUB",
  eur: "EUR",
};

export async function getProducts(currency) {
  const params = new URLSearchParams({ limit: "100" });
  if (currency) {
    params.set("currency", currency);
  }
  const response = await fetch(`/api/products/?${params}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  const data = await response.json();
  return data.products || [];
}

export function formatPrice(price, currency) {
  return `${price} ${CURRENCY_LABELS[currency] || currency.toUpperCase()}`;
}

export async function buyInOneClick(productId, productPriceId, currency) {
  const response = await fetch("/api/buy-in-one-click/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: productId,
      product_price_id: productPriceId,
      currency,
    }),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.error || `API error: ${response.status}`);
  }
  return data;
}