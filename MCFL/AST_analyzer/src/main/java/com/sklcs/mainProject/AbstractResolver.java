package com.sklcs.mainProject;

import java.util.ArrayList;

public abstract class AbstractResolver {

    public ArrayList<String> fileToAnalyze;
    public AbstractParser parser;

    public AbstractResolver(){
        this.fileToAnalyze = new ArrayList<>();
    }

    public void setParser(AbstractParser parser){
        this.parser = parser;
    }

    public void resolve(){
        //for(String filePath: fileToAnalyze){
        //    this.parser.parse(filePath);
        //}
        this.parser.parse(this.fileToAnalyze);
    }

    public ArrayList<String> getFileToAnalyze(){
        return this.fileToAnalyze;
    }

}
