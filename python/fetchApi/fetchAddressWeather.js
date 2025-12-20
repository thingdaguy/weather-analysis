async function fetchAddress(lat, lng) {
  const url =
    `https://nominatim.openstreetmap.org/reverse` +
    `?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;

  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent": "qt-weather-map",
        "Accept-Language": "vi",
      },
    });

    const data = await res.json();
    if (!data || !data.address) return null;

    const addr = data.address;
    const result = {};

    // 👉 CHỈ THÊM FIELD KHI CÓ GIÁ TRỊ
    if (data.display_name) result.full = data.display_name;

    if (addr.state) result.province = addr.state;

    const city = addr.city || addr.town || addr.village;
    if (city) result.city = city;

    const district = addr.suburb || addr.county;
    if (district) result.district = district;

    if (addr.road) result.road = addr.road;

    // ❌ nếu object rỗng → coi như không có địa chỉ
    if (Object.keys(result).length === 0) return null;

    return result;
  } catch (e) {
    console.error("fetchAddress error:", e);
    return null;
  }
}

async function fetchWeather(lat, lng) {
  const url =
    `https://api.open-meteo.com/v1/forecast` +
    `?latitude=${lat}&longitude=${lng}` +
    `&current_weather=true` +
    `&hourly=precipitation` +
    `&daily=temperature_2m_max,temperature_2m_min` +
    `&timezone=auto`;

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (!data.current_weather || !data.daily) return null;

    return {
      temp: data.current_weather.temperature,
      wind: data.current_weather.windspeed,
      precipitation: data.hourly.precipitation[0],
      temp_max: data.daily.temperature_2m_max[0],
      temp_min: data.daily.temperature_2m_min[0],
    };
  } catch {
    return null;
  }
}

async function getLocationWeather(lat, lng) {
  const [address, weather] = await Promise.all([
    fetchAddress(lat, lng),
    fetchWeather(lat, lng),
  ]);

  if (!weather) return null;

  return {
    location: address,
    weather,
  };
}

export { getLocationWeather };
