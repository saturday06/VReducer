 # VRoidモデルの調査メモ
 ## テクスチャ
* 空の法線で使われる (Shader_NoneNormal)
* 空の_EmissionMapで使われる (Shader_NoneBlack)

# VRMモデルの調査メモ
### VRMマテリアルテクスチャ設定
* _SphereAdd: 9, 22 服と髪のリムライト 存在しない場合もある
* _EmissionMap：25 髪のハイライト

### 法線マップの設定フラグ
keywordMapでノーマルマップ、リムライティングのON/OFFができる(キーがなければfalse)
* _NORMALMAP：法線マップ
* MTOON_OUTLINE_COLOR_FIXED：リムライティング
