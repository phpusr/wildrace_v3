<template>
    <v-card :max-height="maxHeight">
        <v-card-title class="flex-nowrap">
            <v-avatar class="elevation-2">
                <img :src="post.author.photo50" alt="" />
            </v-avatar>

            <div class="ml-2">
                <div class="d-flex flex-wrap">
                    <a :href="post.link" target="_blank">#{{post.number}}</a>
                    <span class="mx-1">{{post.author.firstName}}</span>
                    <span>{{post.author.lastName}}</span>
                </div>
                <div class="caption grey--text lighten-3">{{date}}</div>
            </div>

            <post-parser-status :status-id="post.status" class="ml-2" />

            <v-tooltip top v-if="post.lastUpdate">
                <template v-slot:activator="{ on }">
                    <v-btn icon class="blue-grey lighten-4 ml-2" v-on="on">
                        <v-icon>mdi-account-check</v-icon>
                    </v-btn>
                </template>
                <span>{{$t("post.manualEditing")}}</span>
            </v-tooltip>

            <v-spacer />

            <v-btn v-if="userIsAdmin" icon @click="postEditHandler">
                <v-icon>mdi-pencil</v-icon>
            </v-btn>
        </v-card-title>

        <v-card-text>
            <div v-if="post.distance" class="mt-3 display-1 blue--text font-weight-bold">+{{post.distance}}</div>
            <div class="display-1 green--text">{{post.sumDistance}}</div>
            <div class="mt-3 font-italic break-word" v-html="textOfPost" />
        </v-card-text>

        <v-card-actions v-if="largeTextOfPost">
            <v-btn text color="orange" @click="expandPost">{{textExpandPostButton}}</v-btn>
        </v-card-actions>

        <div v-if="post.editReason" class="orange lighten-4 pa-2">
            <span class="font-weight-medium">{{$t("post.editReason")}}:</span>
            {{post.editReason}}
        </div>
    </v-card>
</template>

<script>
    import PostParserStatus from "./PostParserStatus"
    import dateFormat from "date-format"
    import {mapGetters} from "vuex"

    const maxLength = 170
    const maxHeight = 500

    export default {
        components: {PostParserStatus},
        props: {
            post: Object
        },
        data: () => ({
            maxHeight
        }),
        computed: {
            ...mapGetters(["userIsAdmin"]),
            date() {
                return dateFormat("hh:mm dd.MM.yyyy", new Date(this.post.date))
            },
            largeTextOfPost() {
                return this.post.text.length > maxLength
            },
            textExpandPostButton() {
                return this.$t(this.maxHeight ? "post.expand" : "post.squeeze")
            },
            textOfPost() {
                let {text} = this.post
                if (this.maxHeight) {
                    text = text.length > maxLength ? text.substr(0, maxLength) + "..." : text
                }
                return text.replace(/\n/g, "<br/>")
            }
        },
        methods: {
            postEditHandler() {
                this.$router.push({
                    path: `/post/${this.post.id}/edit`,
                    query: this.$route.query
                })
            },
            expandPost() {
                this.maxHeight = this.maxHeight ? null : maxHeight
            }
        }
    }
</script>

<style>
    .break-word {
        word-wrap: break-word;
    }
</style>