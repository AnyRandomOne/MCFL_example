package com.sklcs.mainProject;

import java.io.File;

public class TestFileResolver extends AbstractResolver {
    public TestFileResolver(String filePath){
        super();
        File file = new File(filePath);
        if(!file.exists() || file.isDirectory()){
            System.out.println("please check the input file");
            return;
        }
        this.fileToAnalyze.add(filePath);
        //System.out.println(this.fileToAnalyze);
    }
}
