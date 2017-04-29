# HomePhone
Raspberry Pi等を使った部屋間のインターホン



台所で『ご飯できたよー』が各部屋で聞こえないと，文句を言われるため，
部屋間でアナウンスを流すためのインターホンモドキを作成．

市販品を買わなかった理由はwifi対応のものは非常にお高いため．




## 動作原理
ネットワークの接続状態を監視するdaemonで有効なIPアドレスが
取得できたら，LEDを点けて，pulseaudioのdaemonを起動．

pulseaudioのdaemonはrtpを受信すると再生するように設定ファイルに
書いておく．

もう一つのdaemonでraspberry piのGPIOにつながっているボタンの
状態を監視，ボタンが押されたら，pulseaudioにrtpの送信モジュールを
ロードして，マイクから音声を拾って，pulseaudioに
再生(RTPの送信)をさせるプログラムを呼び出した上，
音声の再生モジュールの音量を最低(ミュート)にする．

ボタンが離されたら，マイクの音を拾うプログラムをkillし，
pulseaudioのrtp送信モジュールをアンロード，
音声再生モジュールのミュートを解除，
最後にLEDを消灯．


## ついでのツール類
dhcpでアドレスを取得するようにしているため，メンテナンスのために
sshでログインするために家のルータに固定DHCPの設定をするのが
面倒だった．

そのため，マルチキャストのあるアドレスを監視し，
そこにUDPが届いたら，自分のホスト名を返信する
daemonを常駐させることとした．

それに対応するコマンド(pingみたいなもの)も
用意し，あるマルチキャストのアドレス(とポート番号)の
ペアにUDPのパケットを送信し，しばらく返信を待ち受け
受信したパケットの発信元のIPアドレスとパケットの中身の
ホスト名をコンソールに出力するプログラムとした．
これで，一発ping風コマンドを叩くと，どの部屋においた
インターホンモドキがどのIPアドレスかわかる．


## 使ったハードウェア
| 種類                    | 機種等                             |
|:------------------------|-----------------------------------:|
| 本体                    | Raspberry Pi3とRaspberry Pi zero W |
| USBサウンド             | [SOUND BLASTER PLAY! 2](http://jp.creative.com/p/sound-blaster/sound-blaster-play-2)|
| アンプ                  | [極小D級アンプモジュール(3W) AMP8002-3W](http://www.aitendo.com/product/4278)|
| スピーカー              | [スピーカユニット(8Ω2W) SPK-8OHM2W](http://www.aitendo.com/product/7478)|
| DC/DC変換               | [LXDC55使用DCDCコンバータキット(5V)](http://akizukidenshi.com/catalog/g/gK-09981/)|
| ACアダプタ              | [スイッチングACアダプター9V2A 100V～240V GF18-US0920-T](http://akizukidenshi.com/catalog/g/gM-02193/)|
| 電源ケーブル            | [カモン 5521-MB](http://www.comon.co.jp/kataban-5.htm)
| zero w用USB変換ケーブル | [SU2-MCH05R](http://ssa.main.jp/USB.html)|


## アプリ
pulseaudioディレクトリとpyaudioディレクトリがあるが，
きちんと動作するのはpulseaudio以下のもののみ．

最初，単純にpyaudioでマイクからの出力(PCM)をUDPで
マルチキャスト宛に送信するアプリを作ってみたが，
pyaudioでUDPを待ち受けて，再生するアプリが
UDPのパケットに気がつくまでの時間が遅く，
喋りはじめ(数秒間)のパケットにをほぼ取りこぼすことと，
アプリの開発に使っていたPi2だと，処理能力不足で
音がブチブチ途切れるため，pyaudioは諦めた(Pi3だと大丈夫)．

そのため，pyaudio以下のプログラムは参考用．




## USBサウンドの問題
pulseaudioのサイトを見ると，マイクの音をrtp(宛先をマルチキャスト)で
送信する場合，なんのアプリも不要でpulseaudioの設定のみでできると
書いてある．

しかし，サウンドブラスターplay2だと，
マイクの音を垂れ流しを開始した直後にpulseaudioがエラーを出して
rtpの送信が止まる．

ぐぐると，『creativeはオープンソースが嫌いなベンダで，敵だ．
技術情報も出さないから安定して動作するものが作れないから使うな』とかいう
書き込みも見られる．

pulseaudioモジュールの中でマイクの音声をそのままrtpで送信するのは
諦めて，pulseaudio付属のアプリ(parecとpacat)で音の取得と
pulseaudioのrtp^sendモジュールへのデータの引き渡しを
行うこととした．

他社のUSBサウンドモジュールだと，pulseaudioのみで
行けるかもしれない．末尾にpulseaudioだけで
やるためのアプリやpulseaudioの設定ファイルの
変更点も付けておきます．(成功したら使えたUSBサウンドモジュールの機種を教えてね :-)

## 準備

まず，alsaの設定でUSBサウンドがデフォルトのサウンドデバイスに
なるようにする．


### /etc/modprobe.d/alsa-base.conf
```
# This sets the index value of the cards but doesn't reorder.
options snd_usb_audio index=0
options snd_bcm2835 index=1

# Does the reordering.
options snd slots=snd_usb_audio,snd_bcm2835
```

次に，pulseaudioの設定

### ~/config/pulse/client.conf
```
autospawn = no
daemon-binary = /bin/true
```

### ~/config/pulse/default.pa

- rtp-recvとnull-sinkデフォルトのサウンドデバイスの設定
- 音量の設定
- デバイス名を入れる

#### デバイス名の調べ方
```
pacmd list-sources
```

```
pacmd list-sinks
```


## インストール
プログラムは全部/usr/local/binに入れる．


## daemon化のための作業

- /var/log/homePhoneディレクトリを作る
- systemdで監視するための設定ファイルの配置とsystemdへの登録


### systemdで監視するための設定ファイルの配置とsystemdへの登録

/etc/defaultに名前を替えて置くファイル
- homePhonePulseReceive-default
- homePhonePulseSendSilent-default
- mppingResponder-default

```
cp homePhonePulseReceive-default    /etc/default/homePhonePulseReceive
cp homePhonePulseSendSilent-default /etc/default/homePhonePulseSendSilent
cp mppingResponder-default          /etc/default/mppingResponder
```

/usr/local/binに置くファイル
- homePhonePulseReceive-start.sh
- homePhonePulseSendSilent-start.sh
- mppingResponder-start.sh
- homePhonePulseReceive-stop.sh
- homePhonePulseSendSilent-stop.sh
- mppingResponder-stop.sh


/etc/systemd/sytemに名前を替えて置くファイル
- homePhonePulseReceive.service-systemd
- homePhonePulseSendSilent.service-systemd
- mppingResponder.service-system


#### まとめて処理する方法

```
for i in homePhonePulseReceive homePhonePulseSendSilent mppingResponder
do
cp $i-default /etc/default/$i
done

cp *.sh /usr/local/bin

for i in homePhonePulseReceive.service homePhonePulseSendSilent.service mppingResponder.service
do
cp $i-systemd /etc/systemd/system/$i
done
```

#### systemdの作業
```
systemctl enable homePhonePulseReceive homePhonePulseSendSilent mppingResponder
```


## ファイルシステムをリードオンリにする
ext4は簡単にはファイルシステムは壊れないが，電源ブチブチすると，
いつか壊れる危険があるため，メンテナンスの時以外はファイルシステムを
リードオンリにすることとした．

### 参考URL
[[メモ] Raspberry Piで OverlayFS (組み込み向け設定・スクリプト)](http://qiita.com/mt08/items/24510d9845b77ef28d8b)

## 参考:まとも?なUSBサウンドモジュールを使う場合
default.paの変更点 サウンドモジュールの名前が当然変わるので
その名前に合わせて
startrtpsendとstoprtpsendを修正

### startrtpsend
parecとpacatの実行部分をコメントアウト

### stoprtpsend
parecをkillしている部分をコメントアウト


