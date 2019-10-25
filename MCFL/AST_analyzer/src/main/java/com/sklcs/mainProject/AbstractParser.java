package com.sklcs.mainProject;

import java.io.File;
import java.io.IOException;

import java.util.ArrayList;

public class AbstractParser {
    //public String reusltFile;
    ParserWriter writer;

    AbstractParser(String resultFile, String[] header, int max_length) throws IOException {
        this.writer = new ParserWriter(resultFile, header, max_length);
    }

    public void parse(String filePath) {
        File file = new File(filePath);
        this.writer.setFileNow(filePath);
        if(file.exists()){
            System.out.println(filePath + "exists");
        }
    }

    public void parse(ArrayList<String> filePathArray){
        for(String fileName: filePathArray){
            //File file = new File(fileName);
            //if(file.exists()){
            //    this.writer.setFileNow(fileName);
            //    System.out.println(fileName + "exists");
            //}
            parse(fileName);
        }
    }
}
