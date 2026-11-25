# List of Apps Tested with versions and date (month/year)

We provide the list of 50 apps and versions we tested in the Tables below.

Among the 50 apps we tested, at least 15 use custom TLS libraries ($\dagger$). Furthermore, among the most popular apps on the Play Store, 9 out of 14 use a custom TLS library. While Snapchat statically links BoringSSL, ByteDance apps CapCut and TikTok bundle their own forks of BoringSSL.

Meta apps, including Facebook, Threads, and Instagram, bundle multiple TLS implementations: each app bundles its own WebView (called Helium) and Fizz-based TLS for regular and MQTT-based transmissions. Notably, we found ChatGPT using the default Conscrypt for text features, but a custom TLS library (WebRTC, `libpeerjingle`) for audio or video. In the Google ecosystem, apps like YouTube and Gemini bundle their own versions of the Cronet TLS library. While YouTube comes pre-installed on the device and cannot be removed, Gemini shares its UID with the Google Quick Search Box app, and replaces it when installed.

Among the SDK-rich apps, we found CastChat using the Agora SDK and the Azure Speech SDK, which bundles its own WebRTC-based TLS libraries; Bejeweled Blitz bundles a game engine library that relies on an OpenSSL implementation, and Speed Camera Detector includes a custom TLS implementation for peer-to-peer transmissions.

Finally, our app set included apps using custom frameworks ($\ddagger$). Uber Eats, which uses React Native, Google Ads and Alibaba, which use Flutter, and Alaska Airlines, which is built using the Xamarin framework.

For all the 50 apps, the APK binaries themselves are not redistributed due to copyright restrictions, but can be obtained from the Google Play Store.

## Popular Apps

| App Name | Advaita | Aosp-Sci | Frida | Mitm |
| --- | --- | --- | --- | --- |
| CapCut $\dagger$ | 16.5.0 (01/26) | 16.3.0 (01/26) | 16.5.0 (01/26) | 16.5.0 (01/26) |
| ChatGPT $\dagger$ | 1.2026.013 (01/26) | 1.2026.020 (01/26) | 1.2026.013 (01/26) | 1.2026.013 (01/26) |
| Facebook $\dagger$ | 549.0.0.61.62 (03/26) | 544.0.0.42.272 (01/26) | 544.0.0.42.272 (01/26) | 544.0.0.42.272 (01/26) |
| Gemini $\dagger$ | 1.0.795460806 (01/26) | 1.0.795460806 (01/26) | 1.0.795460806 (01/26) | 1.0.795460806 (01/26) |
| Instagram $\dagger$ | 418.0.0.51.77 (03/26) | 413.0.0.41.84 (01/26) | 412.0.0.35.87 (01/26) | 412.0.0.35.87 (01/26) |
| PDF Viewer | 2025.5.1 (01/26) | 2025.5.1 (01/26) | 2025.5.1 (01/26) | 2025.5.1 (01/26) |
| SHEIN | 14.1.0 (01/26) | 14.0.6 (01/26) | 14.1.5 (01/26) | 14.1.5 (01/26) |
| Snapchat $\dagger$ | 13.75.0.45 (01/26) | N/A | 13.76.0.46 (01/26) | 13.76.0.46 (01/26) |
| Spotify | 9.1.16.1450 (01/26) | 9.1.16.1450 (01/26) | 9.1.16.1450 (01/26) | 9.1.16.1450 (01/26) |
| Subway Surf | 3.57.1 (01/26) | 3.58.0 (01/26) | 3.57.1 (01/26) | 3.57.1 (01/26) |
| Temu | 4.24.0 (01/26) | 4.20.0 (01/26) | 4.24.0 (01/26) | 4.24.0 (01/26) |
| Threads $\dagger$ | 424.0.0.48.68 (04/26) | 413.0.0.40.83 (01/26) | 413.0.0.40.83 (01/26) | 413.0.0.40.83 (01/26) |
| TikTok $\dagger$ | 43.5.4 (01/26) | 43.5.4 (01/26) | 43.5.4 (01/26) | 43.5.4 (01/26) |
| YouTube $\dagger$ | 21.02.35 (01/26) | 20.51.39 (01/26) | 21.03.36 (01/26) | 21.03.36 (01/26) |

## SDK-Rich Apps

| App Name | Advaita | Aosp-Sci | Frida | Mitm |
| --- | --- | --- | --- | --- |
| AT Player | 20260109 (01/26) | 20260109 (01/26) | 20260109 (01/26) | 20260109 (01/26) |
| Arranger Keyboard | 4.1.3 (01/26) | 4.1.3 (01/26) | 4.1.3 (01/26) | 4.1.3 (01/26) |
| BeReal. | 3.66.0 (01/26) | 3.66.0 (01/26) | 3.66.0 (01/26) | 3.66.0 (01/26) |
| Bejeweled Blitz $\dagger$ | 2.33.1.6 (01/26) | 2.33.1.6 (01/26) | 2.33.1.6 (01/26) | 2.33.1.6 (01/26) |
| CBS Sports | 10.69 (01/26) | 10.69 (01/26) | 10.69 (01/26) | 10.69 (01/26) |
| CastChat $\dagger$ | 2.34.0 (01/26) | 2.34.0 (01/26) | 2.34.0 (01/26) | 2.34.0 (01/26) |
| Cooking City | 3.82.0.5086 (01/26) | 3.82.0.5086 (01/26) | 3.82.0.5086 (01/26) | 3.82.0.5086 (01/26) |
| DIY Boba Tea Drink | 1.0.15 (01/26) | 1.0.15 (01/26) | 1.0.15 (01/26) | 1.0.15 (01/26) |
| Deccan Herald | 3.7.2 (01/26) | 3.7.2 (01/26) | 3.7.2 (01/26) | 3.7.2 (01/26) |
| Differences Game | 1.0.8 (01/26) | 1.0.8 (01/26) | 1.0.8 (01/26) | 1.0.8 (01/26) |
| Dub Music Player | 6.5 (01/26) | 6.5 (01/26) | 6.5 (01/26) | 6.5 (01/26) |
| Fill the Makeup | 1.2 (01/26) | 1.2 (01/26) | 1.2 (01/26) | 1.2 (01/26) |
| Giant Rush! | 1.9.11 (01/26) | 1.9.11 (01/26) | 1.9.11 (01/26) | 1.9.11 (01/26) |
| Listonic | 9.5.3 (01/26) | 9.5.3 (01/26) | 9.5.3 (01/26) | 9.5.3 (01/26) |
| Next SMS | 11.8.3 (01/26) | 11.8.3 (01/26) | 11.8.3 (01/26) | 11.8.3 (01/26) |
| NoClip 2 | 1.144 (01/26) | 1.144 (01/26) | 1.144 (01/26) | 1.144 (01/26) |
| Paper Doll Makeover | 1.6.3 (01/26) | 1.6.3 (01/26) | 1.6.3 (01/26) | 1.6.3 (01/26) |
| PerfectBody | 2.2.4 (01/26) | 2.2.4 (01/26) | 2.2.4 (01/26) | 2.2.4 (01/26) |
| QR Scanner | 17.0 (01/26) | 17.0 (01/26) | 17.0 (01/26) | 17.0 (01/26) |
| Qibla | 15.3 (01/26) | 15.3 (01/26) | 15.3 (01/26) | 15.3 (01/26) |
| Quran Mp3 | 8.3 (01/26) | 8.3 (01/26) | 8.3 (01/26) | 8.3 (01/26) |
| Radio Guatemala | 4.0.78 (01/26) | 4.0.78 (01/26) | 4.0.78 (01/26) | 4.0.78 (01/26) |
| Shmoody | 3.25.0 (01/26) | 3.25.0 (01/26) | 3.25.0 (01/26) | 3.25.0 (01/26) |
| Shopify | 10.2603.0 (01/26) | 10.2603.0 (01/26) | 10.2603.0 (01/26) | 10.2603.0 (01/26) |
| Speed Camera Detector $\dagger$ | 3.2.42 (01/26) | 3.2.41 (01/26) | 3.2.42 (01/26) | 3.2.42 (01/26) |
| StockX | 4.72.0 (01/26) | 4.72.0 (01/26) | 4.72.0 (01/26) | 4.72.0 (01/26) |
| SudoCube | 6.311 (01/26) | 6.311 (01/26) | 6.311 (01/26) | 6.311 (01/26) |
| Super Market Sorting Puzzle | 1.4.4 (01/26) | 1.4.4 (01/26) | 1.4.4 (01/26) | 1.4.4 (01/26) |
| Triangle | 6.4.0 (01/26) | 6.4.0 (01/26) | 6.4.0 (01/26) | 6.4.0 (01/26) |
| Weather | 1.0.64 (01/26) | 1.0.65 (01/26) | 1.0.65 (01/26) | 1.0.65 (01/26) |
| Zillow | 2026.4.0.99082 (01/26) | 2026.5.0.99136 (01/26) | 2026.5.0.99136 (01/26) | 2026.5.0.99136 (01/26) |

### Custom Framework Apps

| App Name | Advaita | Aosp-Sci | Frida | Mitm |
| --- | --- | --- | --- | --- |
| Uber Eats $\dagger$ $\ddagger$ | 6.306.10000 (01/26) | 6.306.10000 (01/26) | 6.306.10000 (01/26) | 6.306.10000 (01/26) |
| Google Ads $\dagger$ $\ddagger$ | 3.21.852023719 (01/26) | 3.21.852023719 (01/26) | 3.21.852023719 (01/26) | 3.21.852023719 (01/26) |
| Alibaba.com $\dagger$ $\ddagger$ | 26.1.2 (01/26) | 26.1.2 (01/26) | 26.1.2 (01/26) | 26.1.2 (01/26) |
| Alaska $\ddagger$ | 7.6.8 (01/26) | 7.6.8 (01/26) | 7.6.8 (01/26) | 7.6.8 (01/26) |

$\dagger$ Apps with custom TLS libraries.
$\ddagger$ Apps using custom frameworks like React, Flutter or Xamarin.
