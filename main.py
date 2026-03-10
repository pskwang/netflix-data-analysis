import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression

# MySQL 연결
engine = create_engine(
    "mysql+mysqlconnector://root@localhost:3306/netflix_db",
    connect_args={"password": "your_password"}
)

df = pd.read_sql("SELECT * FROM netflix_titles", con=engine)
df['year_added'] = pd.to_datetime(df['date_added'], errors='coerce').dt.year

# 넷플릭스 스타일 설정
plt.rcParams['font.family']        = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor']   = '#141414'
plt.rcParams['axes.facecolor']     = '#141414'
plt.rcParams['axes.edgecolor']     = '#333333'
plt.rcParams['axes.labelcolor']    = 'white'
plt.rcParams['xtick.color']        = '#AAAAAA'
plt.rcParams['ytick.color']        = '#AAAAAA'
plt.rcParams['text.color']         = 'white'
plt.rcParams['grid.color']         = '#333333'

RED  = '#E50914'
RED2 = '#B81D24'
GRAY = '#AAAAAA'

# ============================================================
# 기존 대시보드 (6개 그래프)
# ============================================================

fig, axes = plt.subplots(2, 3, figsize=(22, 12))
fig.suptitle('NETFLIX 데이터 분석 대시보드',
             fontsize=20, fontweight='bold', color=RED, y=0.98)
fig.patch.set_facecolor('#141414')

# (1) 콘텐츠 유형 파이차트
ax1 = axes[0, 0]
type_counts = df['type'].value_counts()
wedges, texts, autotexts = ax1.pie(
    type_counts, labels=type_counts.index, autopct='%1.1f%%',
    colors=[RED, '#333333'], startangle=90,
    wedgeprops=dict(edgecolor='#141414', linewidth=2))
for t in texts:
    t.set_color('white'); t.set_fontsize(12)
for at in autotexts:
    at.set_color('white'); at.set_fontsize(11)
ax1.set_title('콘텐츠 유형 비율', color='white', fontsize=13, fontweight='bold', pad=15)

# (2) 연도별 추이
ax2 = axes[0, 1]
yearly = df.groupby('year_added')['type'].count().dropna()
bars = ax2.bar(yearly.index.astype(int), yearly.values,
               color=RED, edgecolor='#141414', linewidth=0.5)
bars[yearly.values.argmax()].set_color('#FF0000')
bars[yearly.values.argmax()].set_edgecolor('white')
ax2.set_title('연도별 콘텐츠 추가 추이', color='white', fontsize=13, fontweight='bold')
ax2.set_xlabel('연도', color=GRAY)
ax2.set_ylabel('콘텐츠 수', color=GRAY)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', alpha=0.3)
ax2.set_facecolor('#141414')

# (3) 장르 TOP 10
ax3 = axes[0, 2]
genre_list = df['listed_in'].dropna().str.split(',').explode().str.strip()
top_genres = genre_list.value_counts().head(10)
ax3.barh(top_genres.index[::-1], top_genres.values[::-1],
         color=RED, edgecolor='#141414')
for i, val in enumerate(top_genres.values[::-1]):
    ax3.text(val * 0.98, i, str(val), va='center', ha='right', color='white', fontsize=9)
ax3.set_title('장르 TOP 10', color='white', fontsize=13, fontweight='bold')
ax3.set_xlabel('콘텐츠 수', color=GRAY)
ax3.grid(axis='x', alpha=0.3)
ax3.set_facecolor('#141414')

# (4) 국가별 TOP 10
ax4 = axes[1, 0]
top_countries = df['country'].replace('', None).dropna().value_counts().head(10)
colors_bar = [RED if i == 0 else '#555555' for i in range(len(top_countries))]
bars4 = ax4.barh(top_countries.index[::-1], top_countries.values[::-1],
                  color=colors_bar[::-1], edgecolor='#141414')
for i, val in enumerate(top_countries.values[::-1]):
    ax4.text(val * 0.98, i, str(val), va='center', ha='right', color='white', fontsize=9)
ax4.set_title('국가별 콘텐츠 TOP 10', color='white', fontsize=13, fontweight='bold')
ax4.set_xlabel('콘텐츠 수', color=GRAY)
ax4.grid(axis='x', alpha=0.3)
ax4.set_facecolor('#141414')

# (5) 시청 등급 분포
ax5 = axes[1, 1]
rating_counts = df[~df['rating'].str.contains('min', na=True)]['rating'].value_counts().head(8)
grad_colors = [RED, RED2, '#8B0000', '#6B0000', '#555555', '#444444', '#333333', '#222222']
ax5.bar(rating_counts.index, rating_counts.values,
        color=grad_colors[:len(rating_counts)], edgecolor='#141414')
ax5.set_title('시청 등급 분포', color='white', fontsize=13, fontweight='bold')
ax5.set_xlabel('등급', color=GRAY)
ax5.set_ylabel('콘텐츠 수', color=GRAY)
ax5.tick_params(axis='x', rotation=30)
ax5.grid(axis='y', alpha=0.3)
ax5.set_facecolor('#141414')

# (6) 감독별 작품 수 TOP 10
ax6 = axes[1, 2]
top_directors = df[
    (df['type'] == 'Movie') &
    (df['director'].notna()) &
    (df['director'] != '')
]['director'].value_counts().head(10)
ax6.barh(top_directors.index[::-1], top_directors.values[::-1],
         color=RED2, edgecolor='#141414')
for i, val in enumerate(top_directors.values[::-1]):
    ax6.text(val * 0.98, i, str(val), va='center', ha='right', color='white', fontsize=9)
ax6.set_title('감독별 작품 수 TOP 10', color='white', fontsize=13, fontweight='bold')
ax6.set_xlabel('작품 수', color=GRAY)
ax6.grid(axis='x', alpha=0.3)
ax6.set_facecolor('#141414')

plt.tight_layout()
plt.savefig('netflix_dashboard.png', dpi=150, bbox_inches='tight', facecolor='#141414')
plt.show()
print("✅ 기본 대시보드 완성!")

# ============================================================
# 동향 분석 (장르 트렌드 + 콘텐츠 예측)
# ============================================================

fig2, axes2 = plt.subplots(1, 2, figsize=(18, 6))
fig2.patch.set_facecolor('#141414')
fig2.suptitle('NETFLIX 동향 분석', fontsize=18, fontweight='bold', color=RED)

# (1) 장르 트렌드
ax1 = axes2[0]
df_genre = df[['year_added', 'listed_in']].dropna()
df_genre['listed_in'] = df_genre['listed_in'].str.split(',')
df_genre = df_genre.explode('listed_in')
df_genre['listed_in'] = df_genre['listed_in'].str.strip()
df_genre = df_genre[df_genre['year_added'] >= 2015]

top5_genres = df_genre['listed_in'].value_counts().head(5).index.tolist()
df_genre_top5 = df_genre[df_genre['listed_in'].isin(top5_genres)]
genre_trend = df_genre_top5.groupby(['year_added', 'listed_in']).size().unstack(fill_value=0)

colors_genre = [RED, '#FF6B6B', '#FF4500', '#B81D24', '#888888']
for i, genre in enumerate(genre_trend.columns):
    ax1.plot(genre_trend.index.astype(int), genre_trend[genre],
             marker='o', linewidth=2.5, label=genre, color=colors_genre[i])
ax1.set_facecolor('#141414')
ax1.set_title('연도별 장르 트렌드 (2015~)', color='white', fontsize=13, fontweight='bold')
ax1.set_xlabel('연도', color=GRAY)
ax1.set_ylabel('콘텐츠 수', color=GRAY)
ax1.legend(fontsize=8, facecolor='#222222', labelcolor='white')
ax1.grid(alpha=0.3)
ax1.tick_params(colors=GRAY)

# (2) 콘텐츠 증가 추세 예측
ax2 = axes2[1]
yearly_total = df.groupby('year_added').size().reset_index(name='count')
yearly_total = yearly_total.dropna().astype(int)
yearly_total = yearly_total[yearly_total['year_added'] >= 2018]

X = yearly_total['year_added'].values.reshape(-1, 1)
y = yearly_total['count'].values

model = LinearRegression()
model.fit(X, y)

# 2022~2025 예측
future_years = np.array([[2022], [2023], [2024], [2025]])
predicted = model.predict(future_years).astype(int)

ax2.set_facecolor('#141414')
ax2.bar(yearly_total['year_added'], yearly_total['count'],
        color=RED, edgecolor='#141414', label='실제 데이터')
ax2.bar([y[0] for y in future_years], predicted,
        color='#555555', edgecolor='#141414', label='예측값', alpha=0.8)

all_years = np.array(list(yearly_total['year_added']) + [y[0] for y in future_years])
trend_line = model.predict(all_years.reshape(-1, 1))
ax2.plot(all_years, trend_line, color='white', linewidth=2, linestyle='--', label='추세선')

ax2.set_title('콘텐츠 증가 추세 예측 (2022~2025)', color='white', fontsize=13, fontweight='bold')
ax2.set_xlabel('연도', color=GRAY)
ax2.set_ylabel('콘텐츠 수', color=GRAY)
ax2.legend(fontsize=9, facecolor='#222222', labelcolor='white')
ax2.grid(axis='y', alpha=0.3)
ax2.tick_params(colors=GRAY)

plt.tight_layout()
plt.savefig('netflix_trend.png', dpi=150, bbox_inches='tight', facecolor='#141414')
plt.show()
print("✅ 동향 분석 완료!")
