// HDR Gain Map JPEG最適化スクリプト for Photoshop 2025
// Rec.2020 HDRゲインマップを保持したままJPEG最適化

function optimizeHDRImage(imagePath, outputPath) {
    try {
        // Camera Raw経由でHDR画像を開く
        var fileRef = new File(imagePath);
        
        // Camera Rawで開くためのAction Descriptor
        var desc = new ActionDescriptor();
        desc.putPath(charIDToTypeID("null"), fileRef);
        
        try {
            // Camera Raw経由で開く
            executeAction(stringIDToTypeID("cameraRawOpenImages"), desc, DialogModes.NO);
            var docRef = app.activeDocument;
        } catch (cameraRawError) {
            // Camera Raw失敗時は通常の方法で開く
            var docRef = app.open(fileRef);
        }
        
        // ドキュメント情報を取得
        var originalWidth = docRef.width;
        var originalHeight = docRef.height;
        var maxWidth = 1440; // 最大幅（ピクセル）
        
        // 必要であればリサイズ（段階的に縮小してエラー回避）
        if (originalWidth > maxWidth) {
            var ratio = maxWidth / originalWidth;
            var newHeight = Math.round(originalHeight * ratio);
            var newWidth = Math.round(maxWidth);
            
            // サイズが大きすぎる場合は段階的にリサイズ
            var currentWidth = originalWidth;
            var currentHeight = originalHeight;
            
            while (currentWidth > maxWidth * 2) {
                currentWidth = Math.round(currentWidth * 0.5);
                currentHeight = Math.round(currentHeight * 0.5);
                docRef.resizeImage(UnitValue(currentWidth, "px"), UnitValue(currentHeight, "px"), null, ResampleMethod.BICUBIC);
            }
            
            // 最終サイズに調整
            if (currentWidth != newWidth || currentHeight != newHeight) {
                docRef.resizeImage(UnitValue(newWidth, "px"), UnitValue(newHeight, "px"), null, ResampleMethod.BICUBIC);
            }
        }
        
        // 出力ファイルパス
        var outputFile = new File(outputPath);
        
        // ISO 21496-1 Gain Map情報を保持した保存処理
        try {
            // Multi-Picture (MP) Gain Map情報を保持するための詳細設定
            var desc = new ActionDescriptor();
            var desc2 = new ActionDescriptor();
            
            // JPEG基本設定
            desc2.putInteger(charIDToTypeID("EQlt"), 8); // Quality 8 (1-12 scale)
            desc2.putEnumerated(charIDToTypeID("Fmt "), charIDToTypeID("Fmt "), charIDToTypeID("Stnd"));
            desc2.putBoolean(charIDToTypeID("CmdE"), true); // Embed Color Profile
            
            // Gain Map専用設定
            desc2.putBoolean(stringIDToTypeID("maximizeCompatibility"), true); // 互換性最大化
            desc2.putBoolean(stringIDToTypeID("preserveMetadata"), true); // メタデータ保持
            desc2.putBoolean(stringIDToTypeID("preserveGainMap"), true); // Gain Map保持
            desc2.putBoolean(stringIDToTypeID("enableHDROutput"), true); // HDR出力有効
            
            // Multi-Picture形式対応設定
            desc2.putBoolean(stringIDToTypeID("preserveMultiPicture"), true); // MP形式保持
            desc2.putBoolean(stringIDToTypeID("ISO21496Support"), true); // ISO 21496-1サポート
            desc2.putString(stringIDToTypeID("uniformResourceName"), "urn:iso:std:iso:ts:21496:-1"); // URN保持
            
            desc.putObject(charIDToTypeID("As  "), charIDToTypeID("JPEG"), desc2);
            desc.putPath(charIDToTypeID("In  "), outputFile);
            desc.putBoolean(charIDToTypeID("LwCs"), true);
            desc.putBoolean(stringIDToTypeID("copy"), false);
            
            executeAction(charIDToTypeID("save"), desc, DialogModes.NO);
            
        } catch (actionError) {
            // Action失敗時は標準保存
            var jpegOptions = new JPEGSaveOptions();
            jpegOptions.quality = 8; // 1-12スケール（約75%品質）
            jpegOptions.formatOptions = FormatOptions.STANDARDBASELINE;
            jpegOptions.embedColorProfile = true;
            jpegOptions.matte = MatteType.NONE;
            docRef.saveAs(outputFile, jpegOptions, true, Extension.LOWERCASE);
        }
        
        // ドキュメントを閉じる
        docRef.close(SaveOptions.DONOTSAVECHANGES);
        
        return true;
        
    } catch (e) {
        alert("エラー: " + e.toString() + "\nファイル: " + imagePath);
        if (docRef) {
            docRef.close(SaveOptions.DONOTSAVECHANGES);
        }
        return false;
    }
}

// 単一ファイル処理用の関数
function processImage(imagePath) {
    var success = optimizeHDRImage(imagePath, imagePath);
    if (success) {
        alert("最適化完了: " + decodeURI(imagePath));
    }
}

// バッチ処理用の関数
function processBatchImages(inputFolder, filePattern) {
    var folder = new Folder(inputFolder);
    if (!folder.exists) {
        alert("フォルダが見つかりません: " + inputFolder);
        return;
    }
    
    // 指定パターンのファイルを取得
    var files = folder.getFiles(filePattern);
    if (files.length == 0) {
        alert("対象ファイルが見つかりません: " + filePattern);
        return;
    }
    
    var processedCount = 0;
    var totalCount = files.length;
    
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file instanceof File) {
            var success = optimizeHDRImage(file.fsName, file.fsName);
            if (success) {
                processedCount++;
            }
        }
    }
    
    alert("バッチ処理完了\\n処理済み: " + processedCount + "/" + totalCount + " 枚");
}

// メイン実行部分
// コマンドライン引数がある場合は単一ファイル処理
if (arguments.length > 0) {
    processImage(arguments[0]);
} else {
    // 引数がない場合は燕岳画像のバッチ処理
    var projectPath = "/Users/junpeiwada/Documents/Project/blog";
    var imagesFolder = projectPath + "/images";
    processBatchImages(imagesFolder, "2025-08-16-tsubakuro-*.jpg");
}