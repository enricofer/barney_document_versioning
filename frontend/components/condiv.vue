<template>
    <section>
        <b-field>
            <b-taginput
                v-model="tags"
                :data="filteredTags"
                autocomplete
                field="fsearch"
                icon="label"
                @add="saveCondiv"
                @remove="saveCondiv"
                :placeholder="$t('Add a share')"
                @typing="getFilteredTags">
                <template v-slot="props">
                    {{props.option.fsearch}}
                </template>
                <template #empty>
                    {{ $t('No shares') }}
                </template>
                <template #selected="props">
                    <b-tag
                        v-for="(tag, index) in props.tags"
                        :key="index"
                        :type="getType(tag)"
                        rounded
                        :tabstop="false"
                        ellipsis
                        closable
                        @close="removeTag(index, $event)">
                        {{tag.ftag}}
                    </b-tag>
                </template>
            </b-taginput>
        </b-field>
    </section>
</template>

<script>
/* eslint-disable */
import VueI18n from 'vue-i18n';

export default {
    name: 'condiv',

    components: {
        VueI18n,
    },

    data() {
        return {
            usersAndGroups: [],
            filteredTags: undefined,
            isSelectOnly: false,
            currentUser: null,
            tags: [],
            publicTag: "@" + this.$t('public')
        }
    },

    mounted () {
        this.$nuxt.$on('Authenticated', this.authenticated)
        this.$nuxt.$on('versionOpened', this.updateTags)
    },

    methods: {
        getFilteredTags(text) {
            this.filteredTags = this.usersAndGroups.filter((option) => {
                return option.fsearch
                    .toString()
                    .toLowerCase()
                    .indexOf(text.toLowerCase()) >= 0
            })
        },

        getType(tag) {
            if (tag.ftag == this.currentUser) {
                return "is-primary"
            } else if (tag.ftag.charAt(0) == '@'){
                return "is-warning"
            } else {
                return "is-light"
            }
        },

        authenticated(user) {
            this.currentUser = user
            this.$axios.$get('/version/auth_objs/').then(res => {
                console.log(res)
                this.usersAndGroups = res.data.filter((option) => {
                    return option.ftag != this.currentUser
                })
                this.usersAndGroups.push({
                    ftag: "@public",
                    fsearch: this.$t("@public Shared with all users")
                })
            })
        },

        saveCondiv(elem) {
            const share = []
            this.tags.forEach(element => {
                share.push (element.ftag)
            });
            this.$nuxt.$emit('share', share)
        },

        removeTag(index,event) {
            this.tags.splice(index,1)
            this.saveCondiv()
        },

        updateTags(v) {
            console.log("v.condiv",v.condiv)
            this.tags = v.condiv
        }
    }
}
</script>