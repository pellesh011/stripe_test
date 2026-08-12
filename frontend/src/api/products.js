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