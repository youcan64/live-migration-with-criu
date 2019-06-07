# CRIUでプロセス単位のライブマイグレーション
## 実験1 単一PC内でのcheckpoint&restore
### 実験1-1 まずはファイル書き込みのないタイプ
- 作成したプログラム

```C
#include <stdio.h>
#include <unistd.h>

int main() {
    int i;
    for(i=0;i<10;i++){
        printf("%d\n",i);
        sleep(1);
    }
}
```
毎秒数値を出力する。

- 本来の出力
```sh
$ rm a.out 
$ rm loop
$ gcc loop.c 
$ ./a.out
0
1
2
3
4
5
6
7
8
9
```

- CRIUを用いる場合

ターミナルを２つ立ち上げる。
1. ターミナルA: プログラム実行用
2. ターミナルB: CRIU操作用

まずはターミナルAでプログラムを起動

```sh
$ ./a.out &
[1] 14117
$ 0
1
2
3
4
```
&オプションによってバックグラウンド実行され、プロセス番号が表示される。

このプロセス番号をターミナルBで入力、checkpointを作成する。
```sh
$ mkdir out
$ sudo criu dump -t 14117 -j -o ./dump.log -D out
```
`-t`でプロセス番号を指定。`-j`はシェルから実行したジョブであることを示す。`-o`でログファイルの出力ファイルを指定。

出力先ディレクトリoutはcheckpoint作成のたびに初期化されるので、いちいちお掃除する必要はなさそう。

outディレクトリ内にcheckpointのイメージファイルが作成されたので、ターミナルAでrestoreしてやる。

```sh
$ sudo criu restore -j -D out
5
6
7
8
9
```
途中から再開することができる。(要検証:restoreしたターミナルがバグる？入力が見えなくなる。)

### 実験1-2 ファイルに書き込むプログラムの場合
このようなPythonプログラムで実験。
```Python
from time import sleep
import os

def main():
    if(os.path.exists("output.txt")):
        os.remove("output.txt")
    f = open("output.txt",'w')
    for i in range(10):
        f.write("{}\n".format(i))
        sleep(1)
    f.close()

if __name__ == "__main__":
    main()
```
今回は標準出力を利用しないので、単一ターミナルで作業が可能。

```sh
$ python write_file.py &
[1] 16743
$ sudo criu dump -t 16743 --shell-job -o ./dump.log -D out
[1]+  強制終了            python write_file.py
$ cat output.txt
$ sudo criu restore -j -D out
$ cat output.txt 
0
1
2
3
4
5
6
7
8
9
$
```
特にエラー等は起こらず。dump後catしてもoutputに何も入っていないのは、Pythonのファイルへの書き込みはバッファに保存されてからまとめて行われるためである。[flush()](http://www.yamamo10.jp/yamamoto/comp/Python/file/index.php)を用いるとバッファに溜め込まず、即座に書き込みされる。

## 実験1-3 カメラから

# 参考にしたサイト
[libcriu でプロセスの checkpoint と restore をやってみる](https://blog.ssrf.in/post/try-checkpoint-and-restore-the-process-with-criu/)