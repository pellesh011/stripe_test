export async function getOrders() {
  const response = await fetch("/api/orders/");
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  const data = await response.json();
  return data.orders || [];
}