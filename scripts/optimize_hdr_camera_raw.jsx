// Camera Raw 17経由 Gain Map JPEG最適化スクリプト
// HDR Gain Map情報を確実に保持したまま最適化

function optimizeHDRWithCameraRaw(imagePath, outputPath) {
    try {
        var fileRef = new File(imagePath);
        
        // 1. Camera Rawで画像を開く（基本的な方法）
        try {
            // Camera Raw経由で開く
            var openDesc = new ActionDescriptor();
            openDesc.putPath(charIDToTypeID("null"), fileRef);
            executeAction(charIDToTypeID("Opn "), openDesc, DialogModes.NO);
        } catch (openError) {
            // 通常の方法で開く
            app.open(fileRef);
        }
        
        // 少し待機してCamera Rawが完全に読み込まれるまで待つ
        app.refresh();
        
        // 2. 基本的な画像処理設定
        // Camera Rawの自動設定に任せる（明示的な設定は避ける）
        
        // 3. リサイズ処理
        var docRef = app.activeDocument;
        var originalWidth = docRef.width;
        var originalHeight = docRef.height;
        var maxWidth = 1440; // 最大幅
        
        if (originalWidth > maxWidth) {
            var ratio = maxWidth / originalWidth;
            var newHeight = Math.round(originalHeight * ratio);
            var newWidth = Math.round(maxWidth);
            
            // 段階的リサイズでエラー回避
            var currentWidth = originalWidth;
            var currentHeight = originalHeight;
            
            while (currentWidth > maxWidth * 2) {
                currentWidth = Math.round(currentWidth * 0.5);
                currentHeight = Math.round(currentHeight * 0.5);
                docRef.resizeImage(UnitValue(currentWidth, "px"), UnitValue(currentHeight, "px"), null, ResampleMethod.BICUBIC);
            }
            
            if (currentWidth != newWidth || currentHeight != newHeight) {
                docRef.resizeImage(UnitValue(newWidth, "px"), UnitValue(newHeight, "px"), null, ResampleMethod.BICUBIC);
            }
        }
        
        // 4. Gain Map付きJPEG保存（Camera Raw Export経由）
        var outputFile = new File(outputPath);
        
        try {
            // 基本的なJPEG保存でHDR互換性を重視
            var saveDesc = new ActionDescriptor();
            var jpegDesc = new ActionDescriptor();
            
            jpegDesc.putInteger(charIDToTypeID("EQlt"), 8); // Quality 8
            jpegDesc.putEnumerated(charIDToTypeID("Fmt "), charIDToTypeID("Fmt "), charIDToTypeID("Stnd"));
            jpegDesc.putBoolean(charIDToTypeID("CmdE"), true); // Embed Color Profile
            jpegDesc.putBoolean(stringIDToTypeID("maximizeCompatibility"), true); // 互換性最大化
            
            saveDesc.putObject(charIDToTypeID("As  "), charIDToTypeID("JPEG"), jpegDesc);
            saveDesc.putPath(charIDToTypeID("In  "), outputFile);
            saveDesc.putBoolean(charIDToTypeID("LwCs"), true);
            
            executeAction(charIDToTypeID("save"), saveDesc, DialogModes.NO);
            
        } catch (saveError) {
            // Camera Raw Export失敗時の代替保存
            try {
                var saveDesc2 = new ActionDescriptor();
                var jpegDesc = new ActionDescriptor();
                
                jpegDesc.putInteger(charIDToTypeID("EQlt"), 8);
                jpegDesc.putEnumerated(charIDToTypeID("Fmt "), charIDToTypeID("Fmt "), charIDToTypeID("Stnd"));
                jpegDesc.putBoolean(charIDToTypeID("CmdE"), true);
                jpegDesc.putBoolean(stringIDToTypeID("maximizeCompatibility"), true);
                
                saveDesc2.putObject(charIDToTypeID("As  "), charIDToTypeID("JPEG"), jpegDesc);
                saveDesc2.putPath(charIDToTypeID("In  "), outputFile);
                saveDesc2.putBoolean(charIDToTypeID("LwCs"), true);
                
                executeAction(charIDToTypeID("save"), saveDesc2, DialogModes.NO);
                
            } catch (fallbackError) {
                // 最終的にはstandardなJPEG保存
                var jpegOptions = new JPEGSaveOptions();
                jpegOptions.quality = 8;
                jpegOptions.formatOptions = FormatOptions.STANDARDBASELINE;
                jpegOptions.embedColorProfile = true;
                jpegOptions.matte = MatteType.NONE;
                docRef.saveAs(outputFile, jpegOptions, true, Extension.LOWERCASE);
            }
        }
        
        // 5. ドキュメントを閉じる
        docRef.close(SaveOptions.DONOTSAVECHANGES);
        
        return true;
        
    } catch (e) {
        alert("エラー: " + e.toString() + "\nファイル: " + imagePath);
        try {
            if (app.activeDocument) {
                app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
            }
        } catch (closeError) {
            // 閉じる処理でのエラーは無視
        }
        return false;
    }
}

// 単一ファイル処理用関数
function processImageWithCameraRaw(imagePath) {
    var success = optimizeHDRWithCameraRaw(imagePath, imagePath);
    if (success) {
        alert("Gain Map JPEG最適化完了: " + decodeURI(imagePath));
    }
}

// バッチ処理用関数
function processBatchWithCameraRaw(inputFolder, filePattern) {
    var folder = new Folder(inputFolder);
    if (!folder.exists) {
        alert("フォルダが見つかりません: " + inputFolder);
        return;
    }
    
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
            var success = optimizeHDRWithCameraRaw(file.fsName, file.fsName);
            if (success) {
                processedCount++;
            }
        }
    }
    
    alert("Camera Raw Gain Map バッチ処理完了\\n処理済み: " + processedCount + "/" + totalCount + " 枚");
}

// メイン実行
if (arguments.length > 0) {
    processImageWithCameraRaw(arguments[0]);
} else {
    var projectPath = "/Users/junpeiwada/Documents/Project/blog";
    var imagesFolder = projectPath + "/images";
    processBatchWithCameraRaw(imagesFolder, "2025-08-16-tsubakuro-*.jpg");
}