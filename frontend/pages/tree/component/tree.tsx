'use client';

import { useState } from "react";
import Avatar from "@/ui/avatar/avatar";
import Carousel from "@/ui/carousel/carousel";
import LinealChart from "@/ui/chart/lineal_chart";
import styles from "./tree.module.css";
import Button from "@/ui/button/button";

type TreeTab = "comments" | "links";

export default function Tree() {
    const [tab, setTab] = useState<TreeTab>("comments");

    return(
     <section className={styles.treeContainer}>
        <TreHeader />
        <TreeOptions tab={tab} onTabChange={setTab} />
        <TreeContent tab={tab} />
    </section>
    )
}

function TreHeader() {
    return(
        <header className={styles.treeHeaderContainer}>
            <img src="demo.jpg" alt="Tree" />
            <div className={styles.treeHeaderOverlay}></div>
            <div className={styles.treeHeaderContent}>
                <h2 className={styles.treeHeaderTitle}>Tree</h2>
                <p className={styles.treeHeaderDescription}>Tree Description</p>
            </div>
        </header>
    )
}

function TreeOptions({ tab, onTabChange }: { tab: TreeTab, onTabChange: (tab: TreeTab) => void }) {
    return(
        <div className={styles.treeOptionsContainer}>
        <TreeOptionsButton active={tab === "comments"} onClick={() => onTabChange("comments")}>Comments</TreeOptionsButton>
        <TreeOptionsButton active={tab === "links"} onClick={() => onTabChange("links")}>Links</TreeOptionsButton>
        </div>
    )
}

function TreeOptionsButton({ children, active, onClick }: { children: React.ReactNode, active: boolean, onClick: () => void }) {
    return(
            <button
                type="button"
                className={styles.treeOptionsButton}
                onClick={onClick}
                aria-pressed={active}
            >
                <span className={styles.treeOptionsButtonText + " " + (active ? styles.treeOptionsButtonTextActive : styles.treeOptionsButtonTextInactive)}>{children}</span>    
            <div 
                className={styles.treeOptionsActiveIndicator + " " + (active ? styles.treeOptionsActiveIndicatorActive : styles.treeOptionsActiveIndicatorInactive)} 
                ></div>
            </button>
    )
}

function TreeContent({ tab }: { tab: TreeTab }) {
    return (
        <Carousel index={tab === "comments" ? 0 : 1} label="Tree content">
            <TreeCommentSection />
            <TreeLinkSection />
        </Carousel>
    )
}

function TreeCommentSection(){
    return(
        <ul className={styles.treeContentContainer}>
            <TextBox />
            <TextBox />
            <TextBox />
            <TextBox />
             <AddTextBox />
        </ul>
    )
} 

function AddTextBox() {
    return(
       
            <Button size="icon-md" variant="tertiary" className={styles.addTextBoxButton}>
                +
            </Button>
    )
}


function TextBox() {
    return(
        <li className={styles.textBoxContainer}>
             <Avatar src="/demo.jpg" alt="Text Box Title" />
             <div className={styles.textBoxContentContainer}>
            <header className={styles.textBoxHeader}>
                <div className={styles.textBoxHeaderText}>
                    <h6 className={styles.textBoxTitle}>Text Box Title</h6>
                    <p className={styles.textBoxDate}>10/10/2020</p>
                </div>
            </header>
            <p className={styles.textBoxContent}>lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
            <a href="#" className={styles.textBoxLink}>Link</a>
            </div>
        </li>
    )
}


const linksPage=[
    {
        title: "spotify",
        svg: ""
    },
    {
        title: "youtube",
        svg: ""
    },
    {
        title: "instagram",
        svg: ""
    },
    {
        title: "twitch",
        svg: ""
    }
]

const followerPoints = mondayFollowers([118, 132, 141, 168, 175, 198, 214]);

function mondayFollowers(followers: number[]) {
    const latestMonday = startOfMonday(new Date());

    return followers.map((count, index) => {
        const date = new Date(latestMonday);
        date.setDate(latestMonday.getDate() - (followers.length - 1 - index) * 7);

        return { date, followers: count };
    });
}

function startOfMonday(date: Date) {
    const monday = new Date(date);
    const weekday = monday.getDay();
    const daysFromMonday = weekday === 0 ? 6 : weekday - 1;

    monday.setDate(monday.getDate() - daysFromMonday);
    monday.setHours(0, 0, 0, 0);

    return monday;
}

function TreeLinkSection(){
    return(
      <div className={styles.treeLinkSectionContainer}>
        <div className={styles.treeLinkSectionHeader}>
            {
                linksPage.map((link) => (
                    <Button key={link.title} size="sm" variant="secondary">
                        +
                    </Button>
                ))
            }

        </div>
        <p className={styles.treeLinkSectionTitle}>Followers</p>
        <LinealChart
            points={followerPoints}
        />
        </div>
    )
}

