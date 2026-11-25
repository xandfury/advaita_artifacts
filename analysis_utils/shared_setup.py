"""
Common utilities/functions for the notebooks
"""

import numpy as np
from scipy.stats import chi2, friedmanchisquare, rankdata, chi2_contingency
from statsmodels.stats.contingency_tables import mcnemar
from itertools import combinations
import scikit_posthocs as sp
import plotly.graph_objects as go
from IPython.display import display, Markdown, HTML
# from markdown import markdown

# list of drs for the gaps figure
GAPS_DR = [
    'Uber',
    'ByteDance',
    'YouTube',
    'Meta',
    'Spotify',
    'Google',
    'Google AdManager',
    'Snapchat',
    'Google Play Store',
    'Google AdMob',
]

FILLS = {
    'Advaita': 'black',
    'Mitm': '#606060',
    'Frida': '#a0a0a0',
    'Aosp-Sci': '#d0d0d0',
}

FONT = dict(size=13)

GAPS_MARKERS = {
    'Advaita': dict(symbol='square', size=9, color='black', line=dict(width=1, color='black')),
    'Mitm': dict(symbol='circle', size=10, color='white', line=dict(width=1.5, color='black')),
    'Frida': dict(symbol='diamond', size=10, color='gray', line=dict(width=1, color='black')),
    'Aosp-Sci': dict(symbol='cross', size=10, color='black', line=dict(width=1.5, color='black')),
}

def mark_print(stat_data):
    # if 'get_ipython' in globals():
    #     display(Markdown(stat_data))
    # else:
    #     display(HTML(markdown(stat_data, extensions=["tables"])))
        # print(stat_data)
    display(Markdown(stat_data))



def plot_glyph_matrix(df, pii_col='pii_type', dr_col='company', vantage_col='vantage_type',
                      show_advaita_advantage=True, title=None,
                      add_highlights=None, remove_highlights=None,
                      remove_pii_types=None,
                      x_spacing=1.1, y_spacing=1):
    add_highlights = add_highlights or set()
    remove_highlights = remove_highlights or set()
    remove_pii_types = remove_pii_types or set()
    vantages = df['vantage_type'].unique()

    plot_df = df.copy()
    if remove_pii_types:
        plot_df = plot_df[~plot_df[pii_col].isin(remove_pii_types)]

    presence = set(zip(plot_df[dr_col], plot_df[pii_col], plot_df[vantage_col]))
    all_drs = sorted(plot_df[dr_col].unique())
    all_piis = sorted(plot_df[pii_col].unique())

    advaita_only = set()
    if show_advaita_advantage:
        for dr in all_drs:
            for pii in all_piis:
                if (dr, pii, 'Advaita') in presence:
                    if not any((dr, pii, vp) in presence for vp in vantages if vp != 'Advaita'):
                        advaita_only.add((dr, pii))
    advaita_only = (advaita_only | add_highlights) - remove_highlights

    offsets = {'Advaita': (-0.2, 0.2), 'Mitm': (0.2, 0.2),
               'Frida': (-0.2, -0.2), 'Aosp-Sci': (0.2, -0.2)}

    shapes = []
    for i_idx, dr in enumerate(all_drs):
        i = i_idx * x_spacing
        for j_idx, pii in enumerate(all_piis):
            j = j_idx * y_spacing
            if (dr, pii) in advaita_only:
                shapes.append(dict(
                    type='rect', x0=i - 0.45, x1=i + 0.45, y0=j - 0.45, y1=j + 0.45,
                    fillcolor='rgba(255, 200, 200, 0.5)',
                    line=dict(width=1, color='red', dash='dot'), layer='below'))

            for vp in vantages:
                if (dr, pii, vp) in presence:
                    ox, oy = offsets[vp]
                    shapes.append(dict(
                        type='rect', x0=i + ox - 0.15, x1=i + ox + 0.15, y0=j + oy - 0.15, y1=j + oy + 0.15,
                        fillcolor=FILLS[vp], line=dict(width=0.5, color='black')))

    fig = go.Figure()
    print(f"height: {len(all_piis) * int(40 * y_spacing)}")
    fig.update_layout(
        shapes=shapes,
        xaxis=dict(tickmode='array',
                   tickvals=[i * x_spacing for i in range(len(all_drs))],
                   ticktext=all_drs,
                   automargin=True,
                   tickangle=45, title=dict(text='Data Recipient<br>'), showgrid=True, gridcolor='lightgrey',
                   zeroline=False),
        yaxis=dict(tickmode='array',
                   tickvals=[i * y_spacing for i in range(len(all_piis))],
                   ticktext=all_piis,
                   ticksuffix='    ', title=dict(text='PII Type Transmitted', standoff=20),
                   ticklabelstandoff=15, showgrid=True, gridcolor='lightgrey', zeroline=False),
        # width=max(700, len(all_drs) * int(40 * x_spacing)),
        width=1100,
        height=max(700, len(all_piis) * int(35 * y_spacing)),
        plot_bgcolor='white',
        font=FONT,
        showlegend=False,
        margin=dict(l=0, b=0, r=30, t=50 if title else 5),
    )

    for vp in vantages:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers', name=vp, showlegend=True,
            marker=dict(size=14, color=FILLS[vp], symbol='square', line=dict(width=1, color='black'))))

    if advaita_only:
        # dotted line as legend entry for advaita-only
        fig.add_trace(go.Scatter(
            x=[None, None], y=[None, None], mode='lines', name='Advaita-only',
            showlegend=True,
            line=dict(color='red', width=3, dash='dot'),
        ))

    return fig


def dr_stream_scatter(stream_pivot, vantage_types, font):
    fig = go.Figure()

    # drs = stream_pivot.index.tolist()
    drs = sorted(stream_pivot.index.tolist())
    for vp in vantage_types:
        m = GAPS_MARKERS[vp]
        vals = []
        for dr in drs:
            v = int(stream_pivot.loc[dr, vp]) if vp in stream_pivot.columns else 0
            vals.append(v if v > 0 else None)  # None hides zero points

        fig.add_trace(go.Scatter(
            x=[f"{s} " for s in drs],
            y=vals,
            mode='markers',
            name=vp,
            marker=dict(
                symbol=m['symbol'],
                size=m['size'],
                color=m['color'],
                line=m['line'],
            ),
        ))

    fig.update_layout(
        yaxis_title="HTTP Streams Captured (Log Scale)",
        xaxis_title="Data Recipient",
        yaxis=dict(
            type='log',
            gridcolor='lightgray',
            showgrid=True, zeroline=False,
            dtick=1,
        ),
        xaxis=dict(
            tickangle=45,
            showgrid=True, gridcolor='lightgrey', zeroline=False
        ),
        plot_bgcolor='white',
        font=font,
        width=max(600, len(drs) * 55),
        height=600,
        margin=dict(l=20, r=0, b=20, t=20),
        legend=dict(
            yanchor="top", y=0.99,
            xanchor="right", x=1.20,
        ),
    )

    return fig

LIB_MAP = {
    # system apps
    '/apex/com.android.conscrypt/lib64/libcrypto.so': 'Android System (Conscrypt)',
    '/apex/com.android.conscrypt/lib64/libssl.so': 'Android System (Conscrypt)',
    # gms
    '/data/app/~~-Ec2aJEgYxfRdFtf3hC91w==/com.google.android.gms-UQgRC4HLUaSCjO2hOcdkjg==/base.apk!/lib/arm64-v8a/libconscrypt_gmscore_jni.so': "GMS (Conscrypt)",
    '/data/app/~~t7NRyTXQHp1o_9YdgRx3og==/com.google.android.gms-ASXdKCN4BVhoQP2oCqJ6AA==/base.apk!/lib/arm64-v8a/libconscrypt_gmscore_jni.so': "GMS (Conscrypt)",
    '/data/app/~~-Ec2aJEgYxfRdFtf3hC91w==/com.google.android.gms-UQgRC4HLUaSCjO2hOcdkjg==/split_CronetDynamite_installtime.apk!/lib/arm64-v8a/libcronet.143.0.7445.0.so': "GMS (Cronet)",
    '/data/app/~~2H4T0HOn_fd8O6QmEr3mPA==/com.google.android.gms-kEbfMU2uqj9tHN64TVMmFg==/base.apk!/lib/arm64-v8a/libconscrypt_gmscore_jni.so': "GMS (Conscrypt)",
    '/data/app/~~2H4T0HOn_fd8O6QmEr3mPA==/com.google.android.gms-kEbfMU2uqj9tHN64TVMmFg==/split_CronetDynamite_installtime.apk!/lib/arm64-v8a/libcronet.144.0.7509.3.so': "GMS (Cronet)",
    '/data/app/~~SmBc1hrVCOmX4T-oYcVITw==/com.google.android.gms-dS-DWblyK5rPc28dncz_PQ==/base.apk!/lib/arm64-v8a/libconscrypt_gmscore_jni.so': "GMS (Conscrypt)",
    '/data/app/~~SmBc1hrVCOmX4T-oYcVITw==/com.google.android.gms-dS-DWblyK5rPc28dncz_PQ==/split_CronetDynamite_installtime.apk!/lib/arm64-v8a/libcronet.144.0.7500.8.so': "GMS (Cronet)",
    '/data/app/~~t7NRyTXQHp1o_9YdgRx3og==/com.google.android.gms-ASXdKCN4BVhoQP2oCqJ6AA==/split_CronetDynamite_installtime.apk!/lib/arm64-v8a/libcronet.145.0.7582.0.so': "GMS (Cronet)",
    '/data/app/~~bWHpIXHAuMjjI4IiNPYpMQ==/com.google.android.gms-JHjv7BI4aYRt-kecO54Kgg==/split_CronetDynamite_installtime.apk!/lib/arm64-v8a/libcronet.146.0.7680.144.so': "GMS (Cronet)",

    # playstore
    '/data/app/~~R6TK_sEPD8BzY-72GeVzXQ==/com.android.vending-cmQ0kkgLr9OqhVUwgQQccw==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libcronet.144.0.7509.3.so': "Google Play (Cronet)",

    # youtube
    '/data/app/~~9K2P7PT-jI9l5S9tnTIp0g==/com.google.android.youtube-iYYayVX4mQHk-DER3GrCsg==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libcronet.144.0.7509.3.so': "YouTube (Cronet)",
    '/data/app/~~vIzUSbHutAMscdYH_w1mbQ==/com.google.android.youtube-4pzad9nWRwtNfw6RHre6Aw==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libcronet.144.0.7509.3.so': "YouTube (Cronet)",
    '/data/app/~~WChC-0vWlZI5QUo3EEQ8Qw==/com.google.android.youtube-jCNjcLVdZhACVo39dEN8rg==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libcronet.145.0.7582.0.so': "YouTube (Cronet)",
    # adwords
    '/data/app/~~LmRdkjvShiHgponBLa31ag==/com.google.android.apps.adwords-haRJzGIE-FHy_5TDe2dUSg==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libflutter.so': "Adwords (Flutter)",
    # quicksearch
    '/data/app/~~Fc6KnL7v000TJ0ozxLjkaw==/com.google.android.googlequicksearchbox-oRAzN3A9mwwchVbcvBlqdA==/base.apk!/lib/arm64-v8a/libcronet.145.0.7582.0.so': "Google QuickSearch (Cronet)",
    '/data/app/~~YigEaXm0ejmx87lCMkV6MA==/com.google.android.googlequicksearchbox-Wd0AABkbvI7Fr8cKE30vzQ==/base.apk!/lib/arm64-v8a/libcronet.144.0.7509.3.so': "Google QuickSearch (Cronet)",
    '/data/app/~~ddW3tI43hKEmxgJo95haWA==/com.google.android.googlequicksearchbox-yJKdMEEvGXhcd1RWoPy0fQ==/base.apk!/lib/arm64-v8a/libcronet.145.0.7608.0.so': "Google QuickSearch (Cronet)",
    '/data/app/~~SMoNDVOJtyUjMfyL3b3lbA==/com.google.android.googlequicksearchbox-ZlDmcSneovwe9XGJgPsZSw==/base.apk!/lib/arm64-v8a/libcronet.145.0.7608.0.so': "Google QuickSearch (Cronet)",

    # talkback
    '/data/app/~~nMSnq-uWdX1Q6MKZdt966g==/com.google.android.tts-Y3FWhChWsZAJo2weITCgnA==/lib/arm64/libcronet.144.0.7500.8.so': "Android - Google Text to Speech (Cronet)",

    # snapchat
    '/data/app/~~6OAAwBXGRMH_8z871QYk6g==/com.snapchat.android-D2D4y3yuciURFIu9u95Xsw==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libclient.so': "Snapchat (Static BoringSSL)",
    '/data/app/~~Sk7X5ZzzaU_EdvLOKhiFFw==/com.snapchat.android-pSTNoKZVd7VBCibv1_ykdw==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libclient.so': "Snapchat (Static BoringSSL)",

    # tiktok
    '/data/app/~~VV37z2e9toGN0P2nNFB3lA==/com.zhiliaoapp.musically--8mlQOBD1BMfnsuTC4s5DA==/lib/arm64/libttcrypto.so': "TikTok (BoringSSL)",
    '/data/app/~~goMSBzxyMfdX_esmopOYoQ==/com.zhiliaoapp.musically-ILvEeY-VFfB6jk4msEYQvw==/lib/arm64/libttcrypto.so': "TikTok (BoringSSL)",
    '/data/app/~~dgMsNdJVlQJ9xZ3S3NPTIg==/com.lemon.lvoverseas-FglksQZdvSBjvtC9bg75_w==/lib/arm64/libttcrypto.so': "CapCult (BoringSSL)",
    '/data/data/com.instagram.android/lib-compressed/libstartup.so': "Meta (Instagram - Fizz)",
    '/data/data/com.facebook.katana/lib-compressed/libcoldstart.so': "Meta (Facebook - Fizz)",
    'advaita_webview': 'Android WebView (Static BoringSSL)',
    '/data/app/~~zwI5a-d09O4Dg3YRsbXYkg==/com.ubercab.eats-_l1nOzY5SCeyhc5blhyv8g==/split_config.arm64_v8a.apk!/lib/arm64-v8a/libcronet.129.0.6668.102.so': "Uber Eats (Cronet)"
}


def map_libs(df):
    # all_libs = set(df['tls_lib'].to_list())
    # if all_libs.difference(LIB_MAP.keys()):
    #     print(f"WARN: no labels found for tls libraries {all_libs.difference(LIB_MAP.keys())}")
    # http_stream_type
    df["tls_lib_label"] = df["tls_lib"].map(LIB_MAP)
    return df